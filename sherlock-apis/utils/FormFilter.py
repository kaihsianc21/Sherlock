def label_parms_filter(request):
    bucket_name = request.form.get('bucket_name')
    bucket_prefix = request.form.get('bucket_prefix')
    model_name = request.form.get('model_name')
    parms = {
        'bucket_name': bucket_name,
        'bucket_prefix': bucket_prefix,
        'model_name': model_name
    }
    return parms
    

def retrain_parms_filter(request):
    bucket_name = request.form.get('bucket_name')
    bucket_prefix = request.form.get('bucket_prefix')
    nb_epoch = request.form.get('nb_epoch')
    batch_size = request.form.get('batch_size')
    model_name = request.form.get('model_name')
    parms = {
        'bucket_name': bucket_name,
        'bucket_prefix': bucket_prefix,
        'nb_epoch': nb_epoch,
        'batch_size': batch_size,
        'model_name': model_name
    }
    return parms


def transfer_parms_filter(request):
    bucket_name = request.form.get('bucket_name')
    bucket_prefix = request.form.get('bucket_prefix')
    model_name = request.form.get('model_name')
    parms = {
        'bucket_name': bucket_name,
        'bucket_prefix': bucket_prefix,
        'model_name': model_name
    }
    return parms