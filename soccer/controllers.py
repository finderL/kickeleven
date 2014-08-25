#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2014-1-23

@author: nttdocomo
'''
import web,os
from PIL import Image
from settings import STATIC_DIR

class hello:
    def GET(self, name):
        #session = web.config.session
        #render = web.template.render('templates', globals={'login': hasattr(session, 'login') and session.login})
        render = web.template.render('templates')
        return render.index()

class Images:
    def GET(self, path):
        path_list = path.split("/")
        resources_path = os.path.join(STATIC_DIR, 'resources')
        image_path = origin_path = os.path.join(resources_path, path_list[0]) + '/' + path_list[1]
        if len(path_list) == 3:
            size = path_list[1].split("_")
            origin_path = os.path.join(resources_path, path_list[0]) + '/' + path_list[2]
            image_path = os.path.join(resources_path, path_list[0] + '/' + path_list[1]) + '/' + path_list[2]
        try:
            im = Image.open(image_path)
        except IOError as e:
            im = Image.open(origin_path)
            if size is not None:
                size = (int(size[0]),int(size[1]))
                thumb_dir = os.path.join(resources_path, path_list[0] + '/' + path_list[1])
                if not os.path.exists(thumb_dir):
                    os.makedirs(thumb_dir)
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(image_path)
        except ValueError:
            print "Could not convert data to an integer."
        except:
            print "Unexpected error:"
            raise
        web.header('Content-type', 'image/png')
        seconds_valid = 24*3600*31
        web.header('Cache-Control', 'max-age=%d' % seconds_valid)
        return open(image_path,"rb").read()