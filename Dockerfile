# Simple Dockerfile to build a REST demo image

FROM grahamdumpleton/mod-wsgi-docker:python-3.5-onbuild
USER $MOD_WSGI_USER:$MOD_WSGI_GROUP

# specify WSGI application file
CMD [ "restdemo.wsgi" ]

