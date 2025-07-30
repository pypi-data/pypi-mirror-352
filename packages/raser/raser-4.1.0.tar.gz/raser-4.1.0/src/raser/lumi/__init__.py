import logging

def main(kwargs):
    label = kwargs['label']
    verbose = kwargs['verbose'] 

    if verbose == 1: # -v 
        logging.basicConfig(level=logging.INFO)
    if verbose == 2: # -vv 
        logging.basicConfig(level=logging.DEBUG)

    logging.info('This is INFO messaage')
    logging.debug('This is DEBUG messaage')

    if label == 'GetDSPprep':
        from . import cflm_p1
        cflm_p1.main()
    if label == 'GetDSPcurrent':
         from . import get_current_p1
         get_current_p1.main()
    if label == 'GetDSPpoicurrent':
        from . import poisson_generator_p1
        poisson_generator_p1.main()

    if label == 'GetCurrentP3_prep':
        from . import cflm_p3
        cflm_p3.main()
    if label == 'GetCurrentP3':
        from. import poisson_generator_p3
        poisson_generator_p3.main()

