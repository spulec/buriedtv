from oauth import OAuthConsumer, OAuthRequest, OAuthToken, OAuthSignatureMethod_HMAC_SHA1
import httplib

# # Usage:
#
# # Two-legged (for making requests that don't require a user, like /stream/summary.json or /user/create/LOGIN.xml):
# client = JtvClient('XXXXXXXX', 'XXXXXXXXXXXXXXXXXXX')
# response = client.get('/stream/summary.xml')
# print response.read()
#
# # Three-legged (after authenticating a user, for making requests on that user's behalf like /clip/create.xml or channel/update/LOGIN.json):
# token = OAuthToken('XXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXX') # These are the user's access token and access secret
# client = JtvClient('XXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXX') # These are your application key and secret
# response = client.post('/user/update/LOGIN.xml', {'title': 'NEW TITLE'}, token)
# print response.read()
#
# # Authenticating a user (for getting an access token you can use for three-legged oauth):
# client = JtvClient('XXXXXXXXXXXXX', 'XXXXXXXXXXXXXXXXXXXX') # These are your application key and secret
# request_token, url = client.make_request_token_and_authorization_url("http://www.example.com/on_user_authorized")
# save_token_to_db(request_token)
# redirect_to_or_open_page_in_web_browser(url)
# # later, in your handler for requests to /on_user_authorized
# request_token = lookup_token_in_db_by_key(request['oauth_token'])
# access_token = client.exchange_request_token_for_access_token(request_token)
# response = client.get('/account/whoami.xml', access_token).read()
# whoami = re.compile(r'<login>(\w+)<\/login>').search(response).group(1)
# client.post('/channel/update.xml' % whoami, {'title': 'NEW TITLE FOR %s' % whoami}, access_token)


class JtvClient(object):
    # consumer_key, consumer_secret are your api key and secret as strings
    def __init__(self, consumer_key, consumer_secret):
        self.consumer = OAuthConsumer(consumer_key, consumer_secret)
        self.host = 'api.justin.tv'
        self.port = 80
        if self.port == 80:
            self.authority = self.host
        else:
            self.authority = "%s:%d" % (self.host, self.port)

    # path is the path to the resource you wish to access in the REST API, without the leading /api
    # token is an OAuthToken from the oauth library
    def get(self, path, token=None, prefix="/api"):
        url = "http://%s%s%s" % (self.host, prefix, path)
        request = OAuthRequest.from_consumer_and_token(
            self.consumer,
            token,
            http_method='GET',
            http_url=url
        )
        return self._send_request(request, token)

    # path is the path to the resource you wish to access in the REST API, without the leading /api
    # post_params is a dictionary of key-value pairs to be serialized into the post body
    # token is an OAuthToken from the oauth library
    def post(self, path, post_params, token=None, prefix="/api"):
        url = "http://%s%s%s" % (self.host, prefix, path)
        request = OAuthRequest.from_consumer_and_token(
            self.consumer,
            token,
            http_method='POST',
            http_url=url,
            parameters=post_params
        )
        return self._send_request(request, token)

    # Create a request token and authorization url that will redirect the user to callback_url when they authorize the application
    # returns a [auth_url:string, token:OAuthToken] array where the token is current unauthorized
    # The callback_url will be redirected_to on success with ?oauth_token=XXXXXXXXXXX, so save the token returned here to
    # some persistent store (like a database), and you can mark it as valid when the callback succeeds
    # After you get a validated request token, you can exchange it for an access token (see exchange_request_token_for_access_token)
    def make_request_token_and_authorization_url(self, callback_url):
        response = self.get("/oauth/request_token", prefix="").read()
        token = OAuthToken.from_string(response)
        request = OAuthRequest.from_token_and_callback(token=token, callback=callback_url, http_url='http://%s/oauth/authorize' % self.authority)
        return [token, request.to_url()]

    # Exchange a validated request token for an access token
    def exchange_request_token_for_access_token(self, request_token):
        response = self.get("/oauth/access_token", request_token, prefix="").read()
        return OAuthToken.from_string(response)

    def _send_request(self, request, token=None):
        request.sign_request(OAuthSignatureMethod_HMAC_SHA1(), self.consumer, token)
        conn = self._get_conn()
        if request.http_method == 'POST':
            conn.request('POST', request.http_url, body=request.to_postdata())
        else:
            conn.request('GET', request.http_url, headers=request.to_header())
        return conn.getresponse()

    def _get_conn(self):
        return httplib.HTTPConnection("%s:%d" % (self.host, self.port))
