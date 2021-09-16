import os
from flask import current_app
import xml.etree.ElementTree as et
import json

class SynthesisPlanner:
    time = ['seconds', 's', 'hr', 'min', 'hours', 'minutes']
    mass = ['g', 'mg']
    volume = ['l', 'ml', 'ul']
    temp = ['K', '°C']
    
    def __init__(self):
        self.name = 'test'

    
    @classmethod
    def update_xdl(cls, parameters, xdl_file):
        """Updates XDL from a database entry

        Args:
            parameters (list): pairs of values corresponding to [parameter name, parameter amount]
            xdl_file (JSON file): A JSON file containing an XDL protocol string

        Returns:
            string: A utf-8 encoded XDL string.
        """
        protocol = cls.load_xdl(xdl_file)
        if protocol[0] is None:
            return False, protocol[1]
        else:
            protocol = protocol[0]
            procedure = protocol.findall('Procedure')
            for step in procedure[0]:
                param = step.get('param')
                if param:
                    num = int(param.split('_')[1])
                    parameter = parameters[num]
                    search_term, units = cls.get_units(parameter[0])
                    step.attrib[search_term] = str(parameter[1]) + ' ' + units
                    del step.attrib['param']
            xdl_string = et.tostring(protocol, encoding='UTF-8')
            xdl_string = xdl_string.decode('UTF-8')
            return True, xdl_string

    @classmethod
    def load_xdl(cls, xdl_file):
        xdl_file = os.path.join(current_app.config['PROTOCOL_FOLDER'], xdl_file)
        if xdl_file[-4:] == ".xdl":
            try:
                with open(xdl_file, encoding='UTF-8') as xdl:
                    raw_xdl = xdl.read()
                    protocol = et.fromstring(raw_xdl)
            except (FileNotFoundError, KeyError) as e:
                return (None, str(e))
        else:
            # file must be json
            try:
                with open(xdl_file, encoding='UTF-8') as xdl:
                    raw_file = json.load(xdl)
                    protocol = et.fromstring(raw_file['protocol'])
            except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError) as e:
                return (None, str(e))
        return (protocol,)
    
    @classmethod
    def get_units(cls, units):
        units = units.split('[')[1][:-1]
        if units in cls.time:
            search_term = 'time'
        elif units in cls.mass:
            search_term = 'mass'
        elif units in cls.volume:
            search_term = 'volume'
        elif units in cls.temp:
            search_term = 'temp'
        else:
            search_term = ''
        return search_term, units
    
    @classmethod
    def write_json_from_file(directory, input_fp, output_fp):
        with open(os.path.join(directory, input_fp), 'r', encoding='UTF-8') as file:
            sample_xdl = {'protocol': file.read()}
        with open(os.path.join(directory, output_fp), 'w+', encoding='UTF-8') as file:
            json.dump(sample_xdl, file, ensure_ascii=False, indent=4)