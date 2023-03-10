import io
import json
import logging
import requests
import time
from collections import namedtuple

from py_zipkin.zipkin import zipkin_span
from py_zipkin.encoding import Encoding
from fdk import response


def handler(ctx, data: io.BytesIO=None):
    tracing_context = ctx.TracingContext()
    with zipkin_span(
        service_name=tracing_context.service_name(),
        span_name="Function Handler",
        transport_handler=(
            lambda encoded_span: transport_handler(
                encoded_span, tracing_context
            )
        ),
        zipkin_attrs=tracing_context.zipkin_attrs(),
        encoding=Encoding.V2_JSON,
        binary_annotations=tracing_context.annotations()
    ):
        name = "World"
        logging.getLogger().info("Inside Python function")
        try:
            body = json.loads(data.getvalue())
            name = body.get("name")
        except (Exception, ValueError) as ex:
            logging.getLogger().info('error parsing json payload: ' + str(ex))


        do_work(ctx)
        do_more_work(ctx)
        return response.Response(
            ctx, response_data=json.dumps(
                {"message": "Hello {0}".format(name)}),
            headers={"Content-Type": "application/json"}
        )

# transport handler, needed by py_zipkin
def transport_handler(encoded_span, tracing_context):
    return requests.post(
        tracing_context.trace_collector_url(),
        data=encoded_span,
        headers={"Content-Type": "application/json"},
    )         

def do_work(ctx):
    with zipkin_span(
        service_name=ctx.TracingContext().service_name(),
        span_name="Doing Error Prone work",
        binary_annotations=ctx.TracingContext().annotations()
    ) as example_span_context:
        try:
            logging.getLogger().debug("Doing some complex task")
            time.sleep(0.15)
            # throwing an exception to show how to add error messages to spans
            raise Exception('Request failed')
        except (Exception, ValueError) as error:
            example_span_context.update_binary_annotations(
                {"Error": True, "errorMessage": str(error)}
            )
        else:
            FakeResponse = namedtuple("FakeResponse", "status, message")
            fakeResponse = FakeResponse(200, "OK")
            # how to update the span dimensions/annotations
            example_span_context.update_binary_annotations(
                {
                    "responseCode": fakeResponse.status,
                    "responseMessage": fakeResponse.message
                }
            )            

def do_more_work(ctx):
    with zipkin_span(
        service_name=ctx.TracingContext().service_name(),
        span_name="Do more work",
        binary_annotations=ctx.TracingContext().annotations()
    ) as example_span_context:
        try:
            logging.getLogger().debug("Doing some complex task")
            time.sleep(0.15)
            # throwing an exception to show how to add error messages to spans
            raise Exception('Request failed')
        except (Exception, ValueError) as error:
            example_span_context.update_binary_annotations(
                {"Error": True, "errorMessage": str(error)}
            )
        else:
            FakeResponse = namedtuple("FakeResponse", "status, message")
            fakeResponse = FakeResponse(200, "OK")
            # how to update the span dimensions/annotations
            example_span_context.update_binary_annotations(
                {
                    "responseCode": fakeResponse.status,
                    "responseMessage": fakeResponse.message
                }
            )            