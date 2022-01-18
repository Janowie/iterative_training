import tensorflow.keras


class IterativeModel(tensorflow.keras.Model):

    def __init__(self, **kwargs):
        super(IterativeModel, self).__init__(**kwargs)
        self.compilation_kwargs = {}

    @staticmethod
    def __name__():
        return "IterativeModel"

    @staticmethod
    def __merge_history(history, new_history):
        """
        Merges two history dictionaries. This is a private method!
        :param history: old history
        :param new_history: current history
        :return: dict
        """
        h = {}
        for key in history.keys():
            h[key] = history[key] + new_history[key]
        return h

    def compile(self, **kwargs):
        """
        Compiles a keras.Model instance and stores kwargs

        :param kwargs: same as for keras.Model.compile()
        """
        if not self.compilation_kwargs:
            self.compilation_kwargs = kwargs

        super(IterativeModel, self).compile(**kwargs)

    def load(self, filepath):
        return tensorflow.keras.models.load_model(
            filepath, custom_objects={self.__name__(): self}
        )

    def fit_iterative(self,
                      sampler=None,
                      num_iterations=5,
                      recompile=True,
                      **kwargs):

        """
        Iterative training

        Source: https://keras.io/examples/nlp/active_learning_review_classification/

        :param sampler: Sampler
        :param num_iterations: number of training iterations
        :param recompile: if True, model is compiled after each iteration (starts learning from scratch)
        :param kwargs: kwargs provided for keras.model.fit function
        :return:
        """

        batch_size = kwargs['batch_size'] if kwargs.get('batch_size') else 256
        epochs = kwargs['epochs'] if kwargs.get('epochs') else 50

        train_datagen, val_datagen, test_datagen = sampler.get_data(batch_size)

        # ------------------------------------------------------------------------ #
        # Init with checkpoints passed from user, add functional checkpoint
        callbacks = [callback for callback in kwargs.get("callbacks") or []]
        callbacks.insert(0, tensorflow.keras.callbacks.ModelCheckpoint("best_model.h5", save_best_only=True, verbose=0))

        print("\n")

        print("-" * 30)
        print(" Training")
        print("-" * 30)

        # Run the initial fit, save model
        history = self.fit(x=train_datagen,
                           validation_data=val_datagen,
                           callbacks=callbacks,
                           epochs=epochs,
                           **kwargs)

        for iteration in range(num_iterations):
            # ---------------------------------------------------------------------- #
            # Evaluate current model performance and based on its sampling strategy,
            # add new training data to the current training ones.

            model = tensorflow.keras.models.load_model('best_model.h5')
            train_datagen, val_datagen = sampler.on_training_end(model)

            # Recompile model to start training from beginning
            if recompile is True:
                self.compile(**self.compilation_kwargs)

            new_history = self.fit(x=train_datagen,
                                   validation_data=val_datagen,
                                   callbacks=callbacks,
                                   epochs=epochs,
                                   **kwargs)

            history = self.__merge_history(history, new_history)

        print("\n")

        print("-" * 30)
        print(" Evaluation")
        print("-" * 30)

        model = self.load('best_model.h5')
        results = model.evaluate(test_datagen, batch_size=batch_size, verbose=0)

        print("\nTest results:\n")
        print("binary accuracy \t\t loss")
        print(f"{results[1]} \t\t {results[0]}")

        return history
