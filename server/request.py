def parse_request(data):
    try:
        headers, body = data.split('\r\n\r\n', 1)
        lines = headers.split('\r\n')
        method, path, _ = lines[0].split(' ')
        header_dict = {}
        for line in lines[1:]:
            if ': ' in line:
                key, value = line.split(': ', 1)
                header_dict[key.lower()] = value
        return {
            'method': method,
            'path': path,
            'headers': header_dict,
            'body': body
        }
    except Exception:
        return None