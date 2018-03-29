from __future__ import print_function
import time
import copy



class RateLimitException(Exception):
    pass

cost_per_tx_s = 3
max_cost_tx_s = 10 * cost_per_tx_s
class rate_limited(object):

    def __init__(self, cost_per_tx_s=cost_per_tx_s,
                 max_cost_tx_s=max_cost_tx_s):
        """
        Rate limit a function using the leaky bucket abstraction.


        Parameters
        ----------
        cost_per_tx_s : float, optional
            How much cost does one call incurr. Default 3sec
        max_cost_tx_s : float, optional
            How much total cost can we hold until we say no more? Default 30sec

        Raises
        ------
        RateLimitException
            If rate limit exceeded. Use e.args[0]['min_wait'] or ['max_wait'] to
            identify how long before this function is available again.

        Notes
        -----
            E.g. if we are allowed to make 2500 calls per 24hrs=86400s
            we set cost_per_tx_s = 86400/2500 := 34.56
            and max_cost_tx_s := 86400

        See Also
        --------
        [Pat Wyatt's blog post](https://www.codeofhonor.com/blog/using
        -transaction-rate-limiting-to-improve-service-reliability)


        """
        assert cost_per_tx_s <= max_cost_tx_s, 'max_cost < cost_per_tx, ' \
                                                 'so this function can never ' \
                                                 'be called.'
        self.cost_per_tx_s = cost_per_tx_s
        self.max_cost_tx_s = max_cost_tx_s
        self.empty_time = time.time()

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            if not self.is_rate_limit_exceeded():
                return f(*args, **kwargs)
            else:
                curr_time = time.time()
                raise RateLimitException({'message':'Rate Limit Exceeded',
                                          'min_wait':
                                              self.empty_time +
                                              self.cost_per_tx_s -
                                              self.max_cost_tx_s -
                                              curr_time,
                                          'max_wait':self.empty_time - curr_time
                                        })
        return wrapper

    def is_rate_limit_exceeded(self):
        curr_time = time.time()
        if curr_time > self.empty_time:
            self.empty_time = curr_time
        new_empty_time = self.empty_time + self.cost_per_tx_s
        if new_empty_time - curr_time > self.max_cost_tx_s:
            return True
        self.empty_time = new_empty_time
        return False


class time_wall_and_clock(object):

    def __init__(self, include_output=False, include_input=False):
        """
        Decorates a function to time wall and clock, returning wall and clock
            time as well as input output parameters in a dictionary.
        Parameters
        ----------
        include_output : boolean, optional
            should the output be included? False by default
        include_input : boolean, optional
            should the input be included? False by default

        Returns
        -------
        wdict : dictionary
            keys: 'run_time' 'run_clock' 'args' (input) 'output'
        """
        self.include_output = include_output
        self.include_input = include_input

    def __call__(self, f):

        def wrapper(*args, **kwargs):

            if self.include_input:
                wdict = copy.deepcopy(kwargs)

                if type(args) == list and type(args[0]) == dict:
                    for k in args:
                        wdict[k] = args[k]
                else:
                    wdict['args'] = args
            else:
                wdict = {}

            start_time = time.time()
            start_clock = time.clock()

            # print wdict

            out = f(*args, **kwargs)

            run_time = time.time() - start_time
            run_clock = time.clock() - start_clock

            if self.include_output:
                if type(out) == list and type(out[0]) == dict:
                    for k in out:
                        wdict[k] = out[k]
                else:
                    wdict['output'] = out

            wdict['run_time'] = run_time
            wdict['run_clock'] = run_clock

            return wdict

        return wrapper
