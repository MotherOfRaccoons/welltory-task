import json
import os
import jsonschema


def json_load(fn):
    with open(fn) as f:
        return json.load(f)


def verify(json_dir, schema_dir):
    logs = {}
    for filename in os.listdir(json_dir):
        log = logs[filename] = []
        try:
            data = json_load(json_dir + filename)
            if not data:
                log.append("JSON file is empty.")
                continue

            if 'event' not in data or not data['event']:
                log.append("Event is not specified.")
                continue
            if 'data' not in data or not data['data']:
                log.append("Data is not specified.")
                continue

            event = data['event']
            schema_file = schema_dir + event + '.schema'
            if not os.path.exists(schema_file):
                log.append("Schema doesn't exist for a '" + event + "' event.")
                continue
        except json.decoder.JSONDecodeError as e:
            log.append("Invalid JSON. " + e.args[0])
            continue

        try:
            schema = json_load(schema_file)
        except json.decoder.JSONDecodeError as e:
            log.append("Invalid '" + schema_file + "' schema JSON." + e.args[0])
            continue

        validator = jsonschema.Draft7Validator(schema)
        errors = validator.iter_errors(data['data'])
        for error in errors:
            cause = error.message
            path = error.path
            if path:
                readable_path = "data"
                for i, value in enumerate(path):
                    if isinstance(value, int):
                        readable_path += " (entry " + str(value) + ")"
                    else:
                        readable_path += "/" + str(value)
                cause += " in " + readable_path
            log.append(cause)

    with open('log.txt', 'w') as file:
        for filename, errors in logs.items():
            if errors:
                file.write(filename + "\n")
                for error in errors:
                    file.write("\t - " + error + "\n")
                file.write("\n")


if __name__ == "__main__":
    json_dir = 'task_folder/event/'
    schema_dir = 'task_folder/schema/'
    verify(json_dir, schema_dir)
