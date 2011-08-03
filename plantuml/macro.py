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

__all__ = ["PlantUMLMacro", "PlantUMLRenderer"]


plantuml_img_dir = 'plantumlimg'
class PlantUMLMacro(WikiMacroBase):
    """
    A macro to include a PlantUML Diagrams
    """

    plantuml_jar = Option("plantuml", "plantuml_jar", "", "Path to PlantUML .jar file")
    def __init__(self):
        self.img_dir = os.path.join(os.path.abspath(self.env.path),plantuml_img_dir)
	if not os.path.isdir(self.img_dir):
	    os.makedirs(self.img_dir)
    def get_img_path(self,img_id):
        img_path = os.path.join(self.img_dir,img_id)
	img_path += '.png'
	return img_path
    def is_img_existing(self,img_id):
        img_path = self.get_img_path(img_id)
        return os.path.isfile(img_path)
        
    def write_img_to_file(self,img_id,data):
        img_path = self.get_img_path(img_id)
        open(img_path,'wb').write(data)

    def expand_macro(self, formatter, name, args):
        if args is None:
            return system_message("No UML text defined!")
        if not self.plantuml_jar:
            return system_message("plantuml_jar option not defined in .ini")
        if not os.path.exists(self.plantuml_jar):
            return system_message("plantuml.jar not found: %s" % self.plantuml_jar)
        
        source = str(args.encode('utf-8')).strip()
        img_id = hashlib.sha1(source).hexdigest()
        if not self.is_img_existing(img_id):
            cmd = "java -jar -Djava.awt.headless=true \"%s\" -charset UTF-8 -pipe" % (self.plantuml_jar)
            p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            (stdout, stderr) = p.communicate(input=source)
            if p.returncode != 0:
                return system_message("Error running plantuml: %s" % stderr)

            img_data = stdout
            self.write_img_to_file(img_id,img_data)

        out = "{{{\n#!html\n<img src='%s' alt='PlantUML Diagram' />\n}}}\n" % formatter.href("plantuml", id=img_id)
        return wiki_to_html(out, self.env, formatter.req)


class PlantUMLRenderer(Component):
    implements(IRequestHandler)
    
    ##################################
    ## IRequestHandler
     
    def __init__(self):
        self.img_dir = os.path.join(os.path.abspath(self.env.path),plantuml_img_dir)

    def match_request(self, req):
        return re.match(r'/plantuml?$', req.path_info)

    def process_request(self, req):
        img_id = req.args.get('id')
        img_path = os.path.join(self.img_dir,img_id)
	img_path += '.png'
	img = open(img_path,'rb').read()

        req.send(img, 'image/png', status=200)
        return ""
