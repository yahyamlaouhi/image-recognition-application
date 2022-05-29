from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from PIL import Image
from matplotlib import image
from .forms import ImageForm
from django.core.files.uploadedfile import SimpleUploadedFile
import numpy as np
import tensorflow as tf
import pickle
from skimage.feature import hog
from skimage.color import rgb2gray
import skimage.transform


@login_required(login_url="/login/")
def index(request):

    

    

    form = ImageForm(request.POST or None, request.FILES or None)
    context = {'segment': 'index','form':form,'img_obj':''}

   

    if form.is_valid():
        
        img=form.cleaned_data.get('img')
        img_obj = img
        # image_array=np.array(Image.open(img))
        image_array=skimage.io.imread(img)
        img_batch=np.expand_dims(image_array,0)


        img_features = pipeline_model(image_array)
        MODEL_SVM_poly=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\web application\image_recognition\models\SVM.pickle', 'rb'))
        MODEL_SVM_rbf=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\web application\image_recognition\models\svm_rbf.pickle', 'rb'))
        MODEL_SGD=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\web application\image_recognition\models\sgd.pickle','rb'))
        MODEL_LR=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\web application\image_recognition\models\LR.pickle','rb'))
        MODEL_GNB=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\web application\image_recognition\models\gnb.pickle','rb'))
        MODEL_CNN=tf.keras.models.load_model(r"C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\web application\image_recognition\models\pretrained_CNN_model.h5")
        CLASS_NAMES=['Tomato__Tomato_YellowLeaf__Curl_Virus'
                    ,'Tomato_Bacterial_spot'                         
                    ,'Tomato_Late_blight'                           
                    ,'Tomato_Septoria_leaf_spot'                      
                    ,'Tomato_Spider_mites_Two_spotted_spider_mite'  
                    ,'Tomato_healthy '                                
                    ,'Pepper__bell___healthy '                        
                    ,'Tomato__Target_Spot'                            
                    ,'Pepper__bell___Bacterial_spot'                   
                    ,'Potato___Early_blight'                           
                    ,'Potato___Late_blight'                            
                    ,'Tomato_Early_blight'                             
                    ,'Tomato_Leaf_Mold'                                
                    ,'Tomato__Tomato_mosaic_virus'                     
                    ,'Potato___healthy']


        prediction={"SVM poly":MODEL_SVM_poly.predict(img_features)
        ,"SVM RBF":MODEL_SVM_rbf.predict(img_features)
        ,"SGD":MODEL_SGD.predict(img_features),
        "Logistic Regression":MODEL_LR.predict(img_features),
        "GNB":MODEL_GNB.predict(img_features),
        "Convolutional Neutral Network":CLASS_NAMES[np.argmax(MODEL_CNN.predict(img_batch))]}

        print(prediction)
        context['img_obj']=img_obj
        context['prediction']=prediction
        
    
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
    accuracy_list={"SVM poly":'0.7758035858504281'
        ,"SVM RBF":'0.8270069455661444'
        ,"SGD":'0.8270069455661444',
        "Logistic Regression":'0.7342917137780649',
        "GNB":'0.42303343563236956',
        "Convolutional Neutral Network":'0.9275362491607666'}

    context['accuracy']=accuracy_list

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
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
        



def pipeline_model(img):

    img=skimage.transform.resize(img,(64,64,3))

    # flatten img
    color_features = img.flatten()
    # convert image to grayscale
    gray_image = rgb2gray(img)
    # get HOG features
    hog_features = hog(gray_image, block_norm='L2-Hys', pixels_per_cell=(16, 16))
    # combine color and hog features 
    flat_features = np.hstack([color_features, hog_features])

    scaler=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\PlantVillage\models\scaler.pickle','rb'))

    # # fit the scaler and transform the training features
    feature_stand = scaler.transform(flat_features.reshape(1,-1))

    pca=pickle.load(open(r'C:\Users\USERTEST\Desktop\Mosh\Freelance projects\project\PlantVillage\models\pca.pickle','rb'))

    # pca = PCA(n_components =350)
    feature_stand_pca = pca.transform(feature_stand)

    return feature_stand_pca




