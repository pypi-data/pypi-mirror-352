def main(kwargs):
    label = kwargs['label']
    if label == 'HPK-Si-LGAD-CCE':
        from cce import cce_alpha
        cce_alpha.main()        