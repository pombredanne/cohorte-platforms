#!/usr/bin/python
# -- Content-Encoding: UTF-8 --
"""
COHORTE Node Composer HTTP Service Proxy

:authors: Bassem Debbabi
:copyright: Copyright 2015, isandlaTech
:license:  Apache Software License 2.0
"""

# iPOPO decorators
from pelix.ipopo.decorators import ComponentFactory, Provides, Property, Instantiate, \
    Validate, Invalidate, Requires, RequiresMap, Bind, BindField, UnbindField
import pelix.remote

# Herald
import herald
import herald.beans as beans

# Cohorte 
import cohorte.composer
import cohorte.monitor

# Standard library
import logging
import threading
import json, time, os

# 
import requests

try:
    # Python 3
    import urllib.parse as urlparse

except ImportError:
    # Python 2
    import urlparse

_logger = logging.getLogger("proxy.proxy")

# collecting information 
SUBJECT_GET_HTTP = "cohorte/shell/agent/get_http"

# PROXY SUB PATH
PROXY_SUB_PATH = "/p/"

"""
	TODO: should have a local cache of all information.
"""


@ComponentFactory("cohorte-http-service-proxy-factory")
@Provides(['pelix.http.servlet', herald.SERVICE_DIRECTORY_LISTENER])
@Property('_path', 'pelix.http.path', "/")
@Requires("_directory", herald.SERVICE_DIRECTORY)
@Requires('_herald', herald.SERVICE_HERALD)
@Property('_reject', pelix.remote.PROP_EXPORT_REJECT, ['pelix.http.servlet'])
@Instantiate('cohorte-http-service-proxy')
class HTTPServiceProxy(object):    

    def __init__(self):

        # lock
        self._lock = threading.Lock()

        # servlet's path
        self._path = None

        # herald directory service
        self._directory = None
        self._herald = None        
        
        # list of local isolates
        # peer.uid -> {p_ref, port}
        self._local_isolates = {}

        
    """
    Listeners --------------------------------------------------------------------------------------------------------
    """

    def peer_registered(self, peer):                         
        if peer.name != "cohorte.internals.forker":
            self._add_peer(peer)
            

    def peer_updated(self, peer, access_id, data, previous):
        pass

    def peer_unregistered(self, peer):               
        if peer.name in self._local_isolates:
            with self._lock:
                del self._local_isolates[peer.name]
        
    def load_local_isolates(self):                              
        for p in self._directory.get_peers():                                                    
            self._add_peer(p)
                
    def _add_peer(self, p):
        local_isolate = self._directory.get_local_peer()
        if p.node_uid == local_isolate.node_uid:  
            with self._lock:
                if p.name not in self._local_isolates:    
                    self._local_isolates[p.name] = { 
                                            "p_ref": p, 
                                            "uid" : p.uid,
                                            "port": -1
                                           }
        
    def get_isolate_http_port(self, uid):
        lp = self._directory.get_local_peer()
        if lp.uid != uid:
            msg = beans.Message(SUBJECT_GET_HTTP)
            reply = self._herald.send(uid, msg)
            return reply.content['http.port']
        else:
            # Get the isolate HTTP port
            port = -1
            svc_ref = self._context.get_service_reference(
                pelix.http.HTTP_SERVICE)
            if svc_ref is not None:
                port = svc_ref.get_property(pelix.http.HTTP_SERVICE_PORT)            
            return port
    """
    Servlet (url mapping to rest api) ================================================================
    """

    def do_GET(self, request, response):
        """
        Handle a GET
        """        
        referer = request.get_header('Referer')
        req_path = request.get_path()
        if PROXY_SUB_PATH not in req_path and referer is not None and PROXY_SUB_PATH in referer:
            # case of relative link from a page located in another isolate.
            # request contain a referer of the parent page.
            path, parts = self.get_path(referer)             
            isolate = parts[1]
            intern_isolate_port = self._local_isolates[isolate]["port"]
            if intern_isolate_port == -1 :
                intern_isolate_port = self.get_isolate_http_port(self._local_isolates[isolate]["uid"])
                self._local_isolates[isolate]["port"] = intern_isolate_port            
            intern_url = 'http://localhost:' + str(intern_isolate_port) + req_path
            try:
                r = requests.get(intern_url)                               
                response.send_content(r.status_code, r.content, mime_type=r.headers['content-type'])     
            except:
                response.send_content(501, "Error", "text/html")           
        else:                              
            if req_path.startswith(PROXY_SUB_PATH):
                # link to another isolate
                # e.g., /__proxy/led-gateway-python-auto01/...
                path, parts = self.get_path(request.get_path())                
                isolate = parts[1]
                intern_isolate_port = self._local_isolates[isolate]["port"]
                if intern_isolate_port == -1 :
                    intern_isolate_port = self.get_isolate_http_port(self._local_isolates[isolate]["uid"])
                    self._local_isolates[isolate]["port"] = intern_isolate_port
                intern_url = 'http://localhost:' + str(intern_isolate_port) + "/" + "/".join(parts[2:])                
                try:
                    r = requests.get(intern_url)                                        
                    response.send_content(r.status_code, r.content, mime_type=r.headers['content-type'])                
                except:
                    response.send_content(501, "Error", "text/html")
            else:
                # any other link                
                number = len(self._local_isolates) 
                if number == 0:
                    # no servlets
                    http_content = "<h3>HTTP Services Proxy</h3><ul>"
                    http_content += "<p>This node has no local isolates!</p><p>Please refresh this page to request again the list of local isolates' HTTP proxies.</p>"
                    response.send_content(200, http_content)
                elif number == 1:
                    # redirect automatically to first one
                    to_url = PROXY_SUB_PATH + str(self._local_isolates.keys()[0]) + "/"
                    http_content = "<html><head><meta http-equiv='refresh' content='0; URL=" + to_url + "'/></head><body></body></html>"                                         
                    response.send_content(200, http_content)
                else:    
                    http_content = "<h3>HTTP Services Proxy</h3><ul>"                
                    for isolate in self._local_isolates:
                        http_content += "<li><a href='" + PROXY_SUB_PATH + isolate + "/'>" + isolate + "</a></li>"                    
                    http_content += "</ul>"
                    response.send_content(200, http_content)                
                    

    def do_delete(self, request, response):
        """
		Handle Delete actions
		"""
        pass

    def get_path(self, myurl):        
        o = urlparse.urlparse(myurl)
        path = o.path        
        # prepare query path: remove first and last '/' if exists
        while path[0] == '/':
            path = path[1:]
        while path[-1] == '/':
            path = path[:-1]
        parts = str(path).split('/')               
        return (path, parts)

    """
	iPOPO STUFF --------------------------------------------------------------------------------------------------------
	"""

    @Validate
    def validate(self, context):
        _logger.info("HTTP Service Proxy validated")
        self._context = context
        # load initial list of local isolates (if already created!)        
        self.load_local_isolates()


    @Invalidate
    def invalidate(self, context):
        _logger.info("HTTP Service Proxy invalidated")


    def bound_to(self, path, params):
        """
		Servlet bound to a path
		"""
        _logger.info('Bound to ' + path)
        return True

    def unbound_from(self, path, params):
        """
		Servlet unbound from a path
		"""
        _logger.info('Unbound from ' + path)
        return None