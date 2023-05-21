# swans-identification-backend

Server to analyze images and store them in the archive

Weights should be stored in ./checkpoints/ and can be downloaded via link - https://drive.google.com/file/d/1p58HWvVsYd94MhV7WcnRpKxvev4dEUov/view?usp=share_link

To run:

1. change `NETWORK_CHEKPOINT` environment variable in `CONFIG.env` to point to the desired checkpoint of the neural network
2. run `docker compose up`
