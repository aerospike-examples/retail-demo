A demo retail website, powered by Aerospike, showcasing Key-Value, Graph, and Vector Search.

To run locally:

1. Download the [kaggle fashion dataset](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset)
    1. Place the contents of the `/images/` directory in the `data/images/` directory.
    2. Place the contents of the `/styles/` directory in the `data/styles/` directory.
2. Replace the `config/aerospike/features.replace.conf` and `config/vector/features.replace.conf` with a valid Aerospike feature key file.
    >**Note**
    >
    >The feature key file must have a line item for `vector-service`
3. Create the containers:
    ```bash
    DOCKER_BUILDKIT=0 docker compose up -d
    ```
4. Load data into the database:
    ```bash
    docker exec -it -w /server aerospike-client python3 load_data.py
    ```
    >**Note**
    >
    >This will take some time. It's loading ~44,000 fashion items, creating an embedding for each image, and 100,000 customer profiles 
5. Access the site at http://localhost:4173
