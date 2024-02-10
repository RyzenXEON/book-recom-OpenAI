from flask import Flask,render_template,request
import pickle
import numpy as np
import openai
#open ai key
openai.api_key = '[Open-AI key]' #insert your open ai key here

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:4]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    print(data)
    
    
    explanations = []
    for i in data:
        book_title = i[0]
        prompt = f"Explain the relationship between the book '{user_input}' and '{book_title}'."
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",  # Choose the appropriate engine
            prompt=prompt,
            max_tokens=150  # Adjust as needed
        )
        explanation = response['choices'][0]['text']
        explanations.append(explanation)

    result_data = list(zip(data, explanations))

    print(result_data)

    return render_template('recommend.html', data=result_data)

    # return render_template('recommend.html',data=data)

@app.route('/contact')
def contact_ui():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug= True, host="0.0.0.0", port= 80)
    #app.run(debug = True)