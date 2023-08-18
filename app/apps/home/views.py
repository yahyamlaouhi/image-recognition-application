from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .forms import ImageForm
import numpy as np
import tensorflow as tf
import pickle
from skimage.feature import hog
from skimage.color import rgb2gray
import skimage.io
import skimage.transform

@login_required(login_url="/login/")
def index(request):
    form = ImageForm(request.POST or None, request.FILES or None)
    context = {'segment': 'index', 'form': form, 'img_obj': '', 'prediction': {}}

    if form.is_valid():
        img = form.cleaned_data.get('img')
        img_obj = img
        image_array = skimage.io.imread(img)
        img_batch = np.expand_dims(image_array, 0)
        img_features = pipeline_model(image_array)
        MODEL_SVM_poly = load_pickle_model('SVM.pickle')
        MODEL_SVM_rbf = load_pickle_model('svm_rbf.pickle')
        MODEL_SGD = load_pickle_model('sgd.pickle')
        MODEL_LR = load_pickle_model('LR.pickle')
        MODEL_GNB = load_pickle_model('gnb.pickle')
        MODEL_CNN = tf.keras.models.load_model('pretrained_CNN_model.h5')
        CLASS_NAMES = ['Tomato__Tomato_YellowLeaf__Curl_Virus',
                       'Tomato_Bacterial_spot',
                       'Tomato_Late_blight',
                       # ... (other class names)
                       'Potato___healthy']

        prediction = {
            "SVM poly": MODEL_SVM_poly.predict(img_features),
            "SVM RBF": MODEL_SVM_rbf.predict(img_features),
            "SGD": MODEL_SGD.predict(img_features),
            "Logistic Regression": MODEL_LR.predict(img_features),
            "GNB": MODEL_GNB.predict(img_features),
            "Convolutional Neutral Network": CLASS_NAMES[np.argmax(MODEL_CNN.predict(img_batch))]
        }
        context['prediction'] = prediction

    context['img_obj'] = img_obj
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def dashboard(request):
    context = {'segment': 'dashboard'}
    html_template = loader.get_template('home/dashboard.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def accuracy(request):
    context = {'segment': 'accuracy'}
    accuracy_list = {
        "SVM poly": '0.7758035858504281',
        "SVM RBF": '0.8270069455661444',
        # ... (other accuracy values)
        "Convolutional Neutral Network": '0.9275362491607666'
    }
    context['accuracy'] = accuracy_list
    html_template = loader.get_template('home/accuracy.html')
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def pages(request):
    context = {}
    try:
        load_template = request.path.split('/')[-1]
        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template
        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('home/page-404.html')
    except:
        html_template = loader.get_template('home/page-500.html')
    return HttpResponse(html_template.render(context, request))

def pipeline_model(img):
    img = skimage.transform.resize(img, (64, 64, 3))
    color_features = img.flatten()
    gray_image = rgb2gray(img)
    hog_features = hog(gray_image, block_norm='L2-Hys', pixels_per_cell=(16, 16))
    flat_features = np.hstack([color_features, hog_features])
    scaler = load_pickle_model('scaler.pickle')
    feature_stand = scaler.transform(flat_features.reshape(1, -1))
    pca = load_pickle_model('pca.pickle')
    feature_stand_pca = pca.transform(feature_stand)
    return feature_stand_pca

def load_pickle_model(file_path):
    with open(file_path, 'rb') as file:
        model = pickle.load(file)
    return model
