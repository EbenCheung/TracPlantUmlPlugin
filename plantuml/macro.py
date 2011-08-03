import inspect
import urllib
import hashlib
from StringIO import StringIO

from trac.core import *
from trac.config import Option
from trac.wiki.formatter import wiki_to_html, system_message
from trac.wiki.macros import WikiMacroBase
from trac.web import IRequestHandler, RequestDone
from subprocess import Popen, PIPE
import pickle
import os
import re
import tempfile
import urllib
from datetime import datetime
import base64

__all__ = ["PlantUMLMacro", "PlantUMLRenderer"]

class PlantUMLMacro(WikiMacroBase):
    """
    A macro to include a PlantUML Diagrams
    """

    plantuml_jar = Option("plantuml", "plantuml_jar", "", "Path to PlantUML .jar file")

    def expand_macro(self, formatter, name, args):
        if args is None:
            return system_message("No UML text defined!")
        if not self.plantuml_jar:
            return system_message("plantuml_jar option not defined in .ini")
        if not os.path.exists(self.plantuml_jar):
            return system_message("plantuml.jar not found: %s" % self.plantuml_jar)

        source = args.encode('utf-8').strip()

        try:
            graphs = pickle.loads(base64.b64decode(formatter.req.session.get('plantuml',"")))
        except:
            graphs = {}
            
        img_id = hashlib.sha1(source).hexdigest()            
            
        #Clean old images
        for key, graph in graphs.items():
            if (datetime.now() - graph[1]).seconds > 3600:
                del graphs[key]              

        if not graphs.has_key(img_id):
        
            cmd = "java -jar -Djava.awt.headless=true \"%s\" -charset UTF-8 -pipe" % (self.plantuml_jar)
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = p.communicate(input=source)
            if p.returncode != 0:
                return system_message("Error running plantuml: %s" % stderr)

            graphs[img_id] = (stdout, datetime.now())        
        
        
        formatter.req.session['plantuml'] = base64.b64encode(pickle.dumps(graphs))

        out = "{{{\n#!html\n<img src='%s' alt='PlantUML Diagram' />\n}}}\n" % formatter.href("plantuml", id=img_id)
        return wiki_to_html(out, self.env, formatter.req)


class PlantUMLRenderer(Component):
    implements(IRequestHandler)
    
    ##################################
    ## IRequestHandler
    
    def match_request(self, req):
        return re.match(r'/plantuml?$', req.path_info)

    def process_request(self, req):
        graphs = pickle.loads(base64.b64decode(req.session.get('plantuml', None)))
        
        img, tstamp = graphs[req.args.get('id')]

        #file = req.args.get('file', None)
        #tfile = open(file, "rb")
        req.send(img, 'image/png', status=200)
        #tfile.close()
        #os.unlink(file)
        return ""
        #raise RequestDone
