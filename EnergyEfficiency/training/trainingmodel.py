import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.multioutput import MultiOutputRegressor
import pickle
from sklearn.preprocessing import Normalizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

class trainingmodel:
    def modeltrain(self):
        try:

            data = pd.read_csv("/home/ubuntu/EnergyEfficiency/static/Data/energy_efficiency_04082020_120000.csv")
            #data = pd.read_csv("c:/Nishikanth/EnergyEfficiency/static/Data/energy_efficiency_04082020_120000.csv")

            #Normalize the inputs and set the output

            nr = Normalizer(copy=False)
            X = data.drop(['heating_load','cooling_load'], axis=1)
            X = nr.fit_transform(X)
            y = data[['heating_load','cooling_load']]

            # Train test split

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3, random_state = 123)

            #Create model evaluation function
            def evaluate(model, test_features, test_labels):
                from sklearn.metrics import r2_score
                predictions = model.predict(test_features)
                R2 = np.mean(r2_score(test_labels, predictions))
                #print('R2 score = %.3f' % R2)
                return r2_score


            lr_model=LinearRegression()
            lr_model.fit(X_train, y_train)
            y_pred=lr_model.predict(X_test)
            #R2 score before optimization
            R2_before_lr= evaluate(lr_model, X_test, y_test)
            #print(R2_before_lr)

            #Import decision tree regressor
            from sklearn.tree import DecisionTreeRegressor
            # Create decision tree model
            dt_model = DecisionTreeRegressor(random_state=123)
            # Apply the model
            dt_model.fit(X_train, y_train)
            # Predicted value
            y_pred1 = dt_model.predict(X_test)

            #R2 score before optimization
            R2_before_dt= evaluate(dt_model, X_test, y_test)


            xgb=XGBRegressor()
            xgb_model=MultiOutputRegressor(estimator=xgb)
            final_model=xgb_model.fit(X_train, y_train)
            y_pred5 = xgb_model.predict(X_test)
            r2_gbr=evaluate(xgb_model,X_test, y_test)
            #print(r2_gbr)

            #save pickle file
            #pickle.dump(final_model, open('c:/Nishikanth/EnergyEfficiency/static/Data/Energy.pkl', 'wb'))
            pickle.dump(final_model, open('/home/ubuntu/EnergyEfficiency/static/Data/Energy.pkl', 'wb'))
        except ValueError:

            raise ValueError
        except KeyError:
            raise KeyError
        except Exception as e:
            raise e
