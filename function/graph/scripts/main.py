import sys
import yaml
from string import Template
from function_helper import get_data, copy_template_to_status, copy_custom_code_to_js, copy_javascript_local_import_to_status


varname_data = get_data("varname.yaml")
style_data = get_data("style.yaml")


def main(arguments):
    plugin_type = arguments[0]
    copy_template_to_status(plugin_type)
    copy_javascript_local_import_to_status(plugin_type)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
