This project uses the data from https://www.kaggle.com/competitions/recruit-restaurant-visitor-forecasting
Our task is to forecast the number of visitors to the restaurants which are given for 39 days.
I made a web application where I also provide analytics about the restaurants and also the forecasting.
And deployed the backend in minikube cluster running in aws ec2 instance.
The componenets created in minikube are:
1) Postgres Statefulset
2) Fastapi Deployment
3) Ingress (nginx)
4) Job(which do the preprocessing. Below you can find more details)
Tried to deploy streamlit as front-end in cluster. But faced some issues.
https://github.com/streamlit/streamlit/issues/4001
So, I ran streamlit locally. It connects to the ingress of the cluster.
For which I ran the command for port-forwarding.
```
kubectl port-forward --address 0.0.0.0 svc/ingress-nginx-controller -n ingress-nginx 30005:80
```
Now I can access it at browser as localhost:30005.
For Front-end I ran Streamlit I ran locally. It has two env variables which are backend-end port and host.
<video src='https://github.com/RavitejaBadugu/Visitors_forecasting/blob/develop/streamlit-app-compressed.mp4' width=180/>
Purpose of Job:
This job we need to ran after creating of postgres statefulset.
1) It retrives the data from s3 bucket.
2) It runs the preprocess.py file
3) Runs the saved LSTM model for forecasting and stores the result.
4) Creates the tables in postgres database.
5) Inserts the data into it.

<iframe width="560" height="315" src="https://www.youtube.com/embed/wVIMyEQaJNU" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
