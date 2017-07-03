#!/usr/bin/python
import yaml
import os

def main():
    # Create yaml files  
    file = open("cache.yaml","w")
    file = open("varname.yaml","w")
    file = open("style.yaml","w")

    # Define default values and import user input  
    default_name = 'adei'
    name = raw_input("> Please enter the type of database: [%s] " %default_name)
    if not name:
        name = default_name
    default_time = '2'
    time = raw_input("> Please key in the time polling duration in second: [%s] " %default_time)
    if not time:
        time = default_time
    default_user = 'jack'
    user = raw_input("> Please enter the username for the access into the database: [%s] " %default_user)
    if not user:
        user = default_user
    default_password = 'rose'
    password = raw_input("> Please enter the password for the access into the database: [%s] " %default_password)
    if not password:
        password = default_password    
    default_pw_designer = 'titanic'
    pw_designer = raw_input("> Please key in the password for the access into designer page: [%s] " %default_pw_designer)
    if not pw_designer:
        pw_designer = default_pw_designer
    default_script = 'services/getdata.php'
    script = raw_input("> Please enter the file name for data retrieval: [%s] " %default_script)
    if not script:
        script = default_script    
    default_server = 'http://katrin.kit.edu/adei-katrin/'
    server = raw_input("> Please enter the url for the database: [%s] " %default_server)
    if not server:
        server = default_server
    default_background = 'cps_02.png'
    background = raw_input("> Please key in the background image name: [%s] " %default_background)
    if not background:
        background = default_background
    default_port = '8888'
    port = raw_input("> Please enter the port number: [%s] " %default_port)
    if not port:
        port = default_port    
    default_title = 'My Project'
    title = raw_input("> Please enter the project title: [%s] " %default_title)
    if not title:
        title = default_title

    os.makedirs("static/"+title+"/images")

    # Define a dictionary for the user input  
    config = {
        'type': name,
        'polling': time,
        'username': user,
        'password': password,
        'pw_designer': pw_designer,
        'script': script,
        'server': server,
        'background': background,
        'port': port,
        'title': title,
    }

    # Create config.yaml file and insert the user input  
    with open ("config.yaml","w") as stream:
        stream.write(yaml.dump(config, default_flow_style=False))

    file.close()


if __name__ == "__main__":
    main()
