import tensorflow as tf
        
class PlainAutoEncoder:
    def __init__(self, num_gene, num_protein, num_pheno, GP_MATRIX, PP_MATRIX, pheno_indices, model_directory, optimizer=tf.train.AdamOptimizer()):
        self.model_save_to = model_directory
        self.pheno_indices = pheno_indices
        self.num_gene = num_gene
        self.num_protein = num_protein
        self.num_pheno = num_pheno
        self.GP_MATRIX = GP_MATRIX
        self.PP_MATRIX = PP_MATRIX

        # Define variables in auto encoder
        self.w1 = tf.Variable(tf.truncated_normal(
            [self.num_gene, self.num_protein],
            stddev=0.01), name="w1")
        self.w2 = tf.Variable(tf.truncated_normal(
            [self.num_protein, self.num_pheno],
            stddev=0.01), name="w2")
        self.b2 = tf.Variable(tf.zeros([self.num_pheno]), name='b2')
        self.w3 = tf.Variable(tf.truncated_normal(
            [self.num_pheno, self.num_protein],
            stddev=0.01), name="w3")
        self.b4 = tf.Variable(tf.zeros(
            [self.num_protein]), name='b4')
        self.w4 = tf.Variable(
            tf.truncated_normal([self.num_protein, self.num_gene],
                                stddev=0.01), name="w4")

        # Input, output and optimizer for unsupervised.
        self.gene = tf.placeholder(tf.float32, [None, self.num_gene], name="gene")
        self.reconstruction = self._forward_op(self.gene)
        # TP: loss function here is RMSE (absolute), not relative error.
        self.reconstruction_cost = tf.reduce_sum(tf.pow(tf.subtract(self.reconstruction, self.gene), 2.0))
        self.optimizer1 = optimizer.minimize(self.reconstruction_cost)

        # Input, output and optimizer for supervised.
        self.actual_pheno = tf.placeholder(tf.float32, [None, len(list(self.pheno_indices))], name="growth_rate")

        pheno_layer = self._half_forward_op(self.gene)
        self.pred_pheno = tf.transpose(tf.stack([pheno_layer[:, i] for i in self.pheno_indices]))

        # TP: supervised loss may also need to consider unsupervised loss as a factor.
        self.non_zero_actual_pheno = tf.add(self.actual_pheno, 0.00001*tf.ones(tf.shape(self.actual_pheno))) # Add tiny number to actual phenotype
        # Absolute relative errors
        self.supervised_loss = tf.reduce_sum(tf.abs(tf.div(tf.subtract(self.non_zero_actual_pheno, self.pred_pheno), self.non_zero_actual_pheno)))
        self.optimizer2 = optimizer.minimize(self.supervised_loss, var_list=[self.b2, self.w2])

    def init_variables(self, session):
        self.sess = session
        init_op = tf.initialize_all_variables()
        self.sess.run(init_op)

    def predict_pheno(self, gene):
        return self.sess.run(self.pred_pheno, feed_dict={
            self.gene: gene
        })

    def model_saver(self):
        saver = tf.train.Saver()
        save_path = saver.save(self.sess, self.model_save_to)
        return save_path

    def model_loader(self):
        saver = tf.train.Saver()
        saver.restore(self.sess, self.model_save_to)
        print("Model {} is loaded.".format(self.model_save_to))

    def get_weight_and_bias(self):
        """ Get the weight matrix from protein to phenotype """
        return self.sess.run([tf.transpose(tf.matmul(tf.transpose(self.PP_MATRIX), self.w2))[0], self.b2[0]], feed_dict={})

    def get_reconstruction(self, gene):
        return self.sess.run(self.reconstruction, feed_dict={
            self.gene: gene
        })

    def partial_fit(self, gene):
        """ Unsupervised training on cost """
        cost, opt = self.sess.run((self.reconstruction_cost, self.optimizer1), feed_dict={self.gene: gene})
        return cost

    def supervised_fit(self, gene, pheno):
        cost, opt = self.sess.run((self.supervised_loss, self.optimizer2), feed_dict={self.gene: gene, self.actual_pheno: pheno})
        return cost

    def inspect_tiers(self, gene):
        protein_op = self._protein_op(self.gene)
        growth_rate_op = self._half_forward_op(self.gene)[:, 0]
        results = self.sess.run([protein_op, growth_rate_op], feed_dict={self.gene: gene})
        return results

    """ Operators (private) """

    def _protein_op(self, X):
        return tf.matmul(X, tf.multiply(self.GP_MATRIX, self.w1))

    def _half_forward_op(self, X):
        """ Tensor operator to calcualte phenotype """
        # TP: use tf.nn.tanh, tf.nn.sigmoid etc instead of softplus
        # For more activation functions see https://www.tensorflow.org/versions/r0.11/api_docs/python/nn.html#activation-functions
        protein_encode = self._protein_op(X)
        phenotype = tf.nn.softplus(tf.add(tf.matmul(protein_encode, tf.multiply(self.PP_MATRIX, self.w2)), self.b2))
        return phenotype

    def _forward_op(self, X):
        """ Tensor operator to reconstruct input X """
        phenotype = self._half_forward_op(X)
        protein_decode = tf.nn.softplus(tf.add(tf.matmul(phenotype, tf.multiply(tf.transpose(self.PP_MATRIX), self.w3)), self.b4))
        reconstructed = tf.matmul(protein_decode, tf.multiply(tf.transpose(self.GP_MATRIX), self.w4))  # GP_MATRIX is 0/1 value to filter out unrelated weights.
        return reconstructed
