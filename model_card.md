# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: Vibetron Mk. I  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate 
- What assumptions does it make about the user
- Is this for real users or classroom exploration  

The system recommends songs based on the user's preferred genre, mood, and energy level. Some assumptions incude the idea of the user having a sole favorite genre and favorite mood, not multiple. It also assumes 3 parameters (genre, mood, energy) dictate the user's music taste and recommendations. It also assumes acoustic preference is dichotomous, rather than being range specified. This system is mainly for classroom exploration.
---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

The scoring model takes into consideration the user and song's features: genre, mood, and energy. The model turns these into a score by matching them to the user's inputted preferences. For example, if the mood of the user and song match, the song score goes up by 2, if not, zero. Additionally, the energy score is determined based on the distance between the song's energy level and that of the user. All the individual scores are added for a total song score, which is considered when recommending happens. I had to change the weight of the genre parameter due to its play in recommending irrelevant songs.
---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

There are 23 songs currently in the catalog file with a good amount of them being rock and pop songs. I occasionally added data to make the catalogue more diverse with genres and moods to allow the system to make more accurate recommendations to the user. I would add a year of release as part of the musical taste to account for the time period a user wants to listen music from. 
---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

My system seems to be very well at matching based on multiple parameters. It does not simply filter a single variable such as genre, it also considers mood and energy. Additionally, it operates on continuous variables like energy similarity, ensuring nuanced results instead of a "yes/no" matching when exact preferences do not exist. It also handles edge cases where "conflicting" or "bland" profiles were able to produce logical results. 
---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

One of the biggest struggles and weaknesses that causes the system to behave disproportionally is that most of the numerical features such as danceability, tempo, valence, etc., are never scored and therefore are not taken into account when calculating a score. For example, if a user specifies they like acoustic, the system does not care and would proceed as if the user specified the opposite. Additionally, the energy mechanism can unintentionally recommend songs that are irrelevant, when mood and genre are irrelevant,  since its value is continuous. 
---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested user profiles that had various preferences, mood, and energy. For example, one profile that I tested was a profile that describes a "sad party animal" with preferences in pop, sad music, and high energy level (0.96). I was looking for songs that matched at least two of the preferences and prioritized the mood. I was surprised when I had a top song that was a metal song with high energy. I knew that was irrelevant, so I had to make changes to the weights of the preferences and added much more data to the songs file.
---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

I definitely could add many more features to improve the model. For example, I could add more variables like "year of release", "popularity", etc. and make sure the recommender actually takes them into consideration with a more complex formula. I also could improve diversity among the top results by having a more robust database of songs instead of 20 and adding constraints on the reccommender to ensure various types of music are recommended. 
---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps 

My biggest learning moment during the project was how much impact small design choices - like weighted user preferences - had on the quality of the recommender. Using AI helped me quickly come up with ideas and generate code for the app. It also helped me understand filtering, however, I occasionally double-checked the ouputs of the reccomender with respect to certain inputs to ensure they are accurate and logical. What surprised me most was how simple scoring algorithms can give a personalized "feel" to users. If I were to extend the project, I would incorportate features like real-time listening and a more nuanced scoring method to ensure accuracy and diversity.
