import zlib
import rx
import rx.operators as ops


def compress():
    ''' Compresses an Observable of bytes with gzip-compression

    The incoming elements are compressed in streaming mode until the
    observable completed.

    The source must be an Observable.
    '''

    def _compress(source):
        def on_subscribe(observer, scheduler):
            # gzip compatibility: https://stackoverflow.com/a/22311297/11689551
            compressor = zlib.compressobj(wbits = zlib.MAX_WBITS | 16)

            def on_next(i):
                try:
                    data = compressor.compress(i)
                    observer.on_next(data)
                except Exception as e:
                    observer.on_error(e)

            def on_completed():
                try:
                    data = compressor.flush()
                    observer.on_next(data)
                    observer.on_completed()
                except Exception as e:
                    observer.on_error(e)

            return source.subscribe(
                on_next=on_next,
                on_completed=on_completed,
                on_error=observer.on_error
            )
        return rx.create(on_subscribe)

    return _compress


def decompress():
    ''' Decompresses an Observable of bytes with gzip-compression

    The incoming elements are decompressed in streaming mode until the
    observable completed.

    The source must be an Observable.
    '''
    def _decompress(source):
        def on_subscribe(observer, scheduler):
            # gzip compatibility: https://stackoverflow.com/a/22311297/11689551
            decompressor = zlib.decompressobj(wbits = zlib.MAX_WBITS | 16)

            def on_next(i):
                try:
                    data = decompressor.decompress(i)
                    observer.on_next(data)
                except Exception as e:
                    observer.on_error(e)

            def on_completed():
                try:
                    if not decompressor.eof:
                        observer.on_error(RuntimeError("z.decompress: Invalid state at observable completion"))
                    else:
                        data = decompressor.flush()
                        observer.on_next(data)
                        observer.on_completed()
                except Exception as e:
                    observer.on_error(e)

            return source.subscribe(
                on_next=on_next,
                on_completed=on_completed,
                on_error=observer.on_error
            )
        return rx.create(on_subscribe)

    return _decompress
