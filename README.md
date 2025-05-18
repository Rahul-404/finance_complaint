# Consumer Complaint Classification for Dispute Prediction

This project utilizes Natural Language Processing (NLP) and machine learning techniques to analyze consumer complaints and predict whether a consumer will dispute the resolution. The system processes complaint descriptions and other relevant features to classify complaints as potentially leading to disputes, enabling more efficient customer service and issue resolution.

## Project Overview

The goal of this project is to build an automated system that can:
- Analyze textual complaints.
- Predict whether the complaint will lead to a consumer dispute.
- Prioritize high-risk cases for businesses to address promptly.

By using machine learning models and NLP techniques, the system can identify patterns in consumer complaints and improve decision-making processes in customer support teams.

## Features

- **Text Classification**: Analyzes the content of consumer complaints to classify them into dispute or no-dispute categories.
- **Stratified Model**: Ensures that the model considers class imbalances and maintains accuracy across different complaint types.
- **Efficient Preprocessing**: Handles text data using tokenization, lemmatization, and vectorization (e.g., TF-IDF) for effective learning.
- **Machine Learning Models**: Trains models such as Logistic Regression, Random Forest, SVM, and XGBoost to predict disputes.
- **Deployment**: The trained model can be deployed for real-time predictions in customer service applications.

## Technologies Used

- **Python**: Programming language for model implementation and NLP processing.
- **scikit-learn**: For machine learning models, data preprocessing, and evaluation metrics.
- **NLTK / spaCy**: For text processing, tokenization, lemmatization, and stop-word removal.
- **pandas & NumPy**: For data manipulation and preprocessing.
- **Matplotlib / Seaborn**: For data visualization and model evaluation metrics.
- **Flask/Django (Optional)**: For deploying the trained model as a web service (API).

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/consumer-complaint-dispute-prediction.git
    cd consumer-complaint-dispute-prediction
    ```

2. Create a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

    or create a environment using `environment.yaml`

    ```bash
    conda env create --prefix ./venv -f environment.yaml
    ```

4. Download the dataset (if not included in the repository) and place it in the `/data` folder.

## How It Works

1. **Data Preprocessing**: The complaint data is preprocessed by cleaning and tokenizing the text. Common NLP techniques such as stop-word removal and lemmatization are applied to prepare the data for model training.
   
2. **Feature Engineering**: In addition to the text data, additional features (like complaint type, consumer demographics, and product type) are included to improve the model's accuracy.

3. **Model Training**: Several machine learning models are trained to predict whether a complaint will lead to a dispute. These models are evaluated using accuracy, precision, recall, and F1-score to determine the best-performing model.

4. **Prediction**: Once trained, the model can be used to predict new complaints. It outputs whether the complaint is likely to escalate into a dispute, helping businesses prioritize their responses.

## Running the Project

To train the model and evaluate it:

1. Preprocess the data:
    ```bash
    python preprocess.py
    ```

2. Train the machine learning models:
    ```bash
    python train_model.py
    ```

3. Evaluate model performance:
    ```bash
    python evaluate_model.py
    ```

4. For real-time prediction (optional):
    - You can deploy the trained model via a Flask or Django API for use in a live system.

## Example Usage

Once the model is trained, you can use it to predict whether a new complaint will result in a dispute:

```python
from model import predict_dispute

complaint_text = "I was charged an unauthorized fee on my credit card and nobody is responding to my inquiries!"

# Predict if the complaint will lead to a dispute
prediction = predict_dispute(complaint_text)
print("Will the consumer dispute? ", prediction)
```

## Evaluation Metrics

The model's performance is evaluated using several common metrics:
- **Accuracy**: The proportion of correct predictions (dispute vs. no dispute).
- **Precision**: The proportion of true positives (dispute) among all predicted disputes.
- **Recall**: The proportion of true positives (dispute) among all actual disputes.
- **F1-Score**: The harmonic mean of precision and recall.

## Contributing

Contributions to this project are welcome! If you have any ideas for improvements or find bugs, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

### Contact

- Author: [Rahul Shelke]
- GitHub: [Rahul-404](https://github.com/Rahul-404)
- Email: [rahulshelke981@gmail.com]
