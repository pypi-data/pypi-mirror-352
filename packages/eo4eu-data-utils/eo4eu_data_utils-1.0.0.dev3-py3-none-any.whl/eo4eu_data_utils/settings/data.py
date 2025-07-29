def recover_soft_fail(data, e: Exception):
    """Returns the incoming Data object, having added all
    items in the ``.passed`` field into the ``.failed``
    field; the result is, essentially, it is an empty object.

    :param data: The input data
    :type data: :class:`eo4eu_data_utils.stream.Data`
    :param e: The exception that occured for this function to be called (Ignored by this function)
    :type e: Exception
    :rtype: :class:`eo4eu_data_utils.stream.Data`
    """
    return data.but(
        passed = [],
        failed = data.failed + data.passed
    )


def recover_raise_exc(data, e: Exception):
    """Raises the provided exception. Use this function when
    you want the pipeline to blow up on unexpected errors.
    Not recommended, but possibly useful if you want your
    own exception handling logic.

    :param data: The input data (Ignored by this function)
    :type data: :class:`eo4eu_data_utils.stream.Data`
    :param e: The exception that occured for this function to be called
    :type e: Exception
    """
    raise e


def recover_continue(data, e: Exception):
    """Returns the incoming Data object, unchanged. This makes
    it so, if a pipeline stage fails, it is simply skipped
    and the data is passed to the next stage. This is probably
    dangerous though, as each stage usually expects the previous
    to have finished...

    :param data: The input data
    :type data: :class:`eo4eu_data_utils.stream.Data`
    :param e: The exception that occured for this function to be called (Ignored by this function)
    :type e: Exception
    :rtype: :class:`eo4eu_data_utils.stream.Data`
    """
    return data
