IMAGE_NAME="gcr.io/msds603-eship/msds603-eship/trendcraft"
IMAGE_TAG="latest"

# docker build -t $IMAGE_NAME:$IMAGE_TAG -f build/docker/Dockerfile .

gcloud config set project msds603-eship

# # gcloud builds submit --tag $IMAGE_NAME:$IMAGE_TAG --timeout=1h
# docker push $IMAGE_NAME:$IMAGE_TAG

gcloud builds submit --region=us-west2 --config cloudbuild.yaml

gcloud run deploy trendcraft \
    --image=$IMAGE_NAME:$IMAGE_TAG \
    --platform=managed \
    --region=us-central1 \
    --allow-unauthenticated