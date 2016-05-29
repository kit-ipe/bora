#!/usr/bin/python
import sys, getopt


def main(sensor, mystr):
    #print mystr
    query = mystr.split("#")[1]
    cmds = query.split("&")
    
    db_server = None
    db_name = None
    db_group = None
    for item in cmds:
        #print item
        subtitle = item.split("=")
        #print subtitle
        if subtitle[0].strip() == "db_server":
            db_server = subtitle[1].strip()
        elif subtitle[0].strip() == "db_name":
            db_name = subtitle[1].strip()
        elif subtitle[0].strip() == "db_group":
            db_group = subtitle[1].strip()

    #print query
    
    rest_str = []
    rest_str.append("http://ipepc57.ipe.kit.edu:8888/add")
    rest_str.append(db_server)
    rest_str.append(db_name)
    rest_str.append(db_group)
    rest_str.append(sensor)
    
    print "/".join(rest_str)


if __name__ == "__main__":
   main(sys.argv[1], sys.argv[2])
