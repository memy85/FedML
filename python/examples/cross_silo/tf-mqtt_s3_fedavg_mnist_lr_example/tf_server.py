import tensorflow as tf

import fedml
from fedml import FedMLRunner
from fedml.data.MNIST.data_loader import download_mnist, load_partition_data_mnist
from tf_model_aggregator import TfServerAggregator


def load_data(args):
    download_mnist(args.data_cache_dir)
    fedml.logging.info("load_data. dataset_name = %s" % args.dataset)

    """
    Please read through the data loader at to see how to customize the dataset for FedML framework.
    """
    (
        client_num,
        train_data_num,
        test_data_num,
        train_data_global,
        test_data_global,
        train_data_local_num_dict,
        train_data_local_dict,
        test_data_local_dict,
        class_num,
    ) = load_partition_data_mnist(
        args,
        args.batch_size,
        train_path=args.data_cache_dir + "/MNIST/train",
        test_path=args.data_cache_dir + "/MNIST/test",
    )
    """
    For shallow NN or linear models, 
    we uniformly sample a fraction of clients each round (as the original FedAvg paper)
    """
    args.client_num_in_total = client_num
    dataset = [
        train_data_num,
        test_data_num,
        train_data_global,
        test_data_global,
        train_data_local_num_dict,
        train_data_local_dict,
        test_data_local_dict,
        class_num,
    ]
    return dataset, class_num


class LogisticRegressionModel(tf.keras.Model):
    def __init__(self, input_dim, out_dim, name=None):
        super(LogisticRegressionModel, self).__init__(name=name)
        self.output_dim = out_dim
        self.layer1 = tf.keras.layers.Dense(out_dim, input_shape=(input_dim,), activation="sigmoid")
        self.layer1.build(input_shape=(input_dim,))

    def call(self, x):
        return self.layer1(x)

    def get_config(self):
        return {"output_dim": self.output_dim, "name": self.name}


def create_model(input_dim, out_dim):
    client_model = LogisticRegressionModel(input_dim, out_dim)
    return client_model


def create_model_aggregator(in_model, in_args):
    aggregator = TfServerAggregator(in_model, in_args)
    return aggregator


if __name__ == "__main__":
    # init FedML framework
    args = fedml.init()
    setattr(args, "run_id", "1979")

    # init device
    device = fedml.device.get_device(args)

    # load data
    dataset, output_dim = load_data(args)

    # load model (the size of MNIST image is 28 x 28)
    model = create_model(28 * 28, output_dim)

    # create model aggregator
    aggregator = create_model_aggregator(model, args)

    # start training
    fedml_runner = FedMLRunner(args, device, dataset, model, server_aggregator=aggregator)
    fedml_runner.run()
