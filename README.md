URL Shortener 🔗

A simple and efficient URL shortening service built with FastAPI and MongoDB. This project allows users to shorten long URLs into simple, shareable links.

📋 Table of Contents

-->Features

-->Setup Guidelines

-->Prerequisites

-->Getting Started

-->Setting Up Environment Variables

-->Running the Project

-->How It Works

Features
URL Shortening: Easily convert long URLs into unique, short codes.
Database Integration: Stores short links and their corresponding original URLs(i,e mappings) in a MongoDB database.
FastAPI: Built on a modern, high-performance web framework for Python.
Environment Variables: Securely manages database credentials and other sensitive information.

Setup Guidelines:-
Prerequisites
Before setting up the project ,  ensure  the following  must be installed on  localmachine:
-->Python 3.8+
-->Git

Getting Started:-
1. Clone the Repository:

     <img width="680" height="127" alt="image" src="https://github.com/user-attachments/assets/6afe9044-42b2-42b8-b108-d31e7884a770" />

   code :
          git clone https://github.com/snahanku/url_shortner.git
   
          cd url_shortner

2.  Create a Python Virtual Environment:
     It's a best practice to use a virtual environment to manage project dependencies.

    <img width="693" height="112" alt="image" src="https://github.com/user-attachments/assets/6a001a3b-c45b-419e-8774-f2fce59438a1" />

    code:
          python -m venv .venv

3.  Activate the Virtual Environment:
   
     --> on Windows , 
          <img width="655" height="102" alt="image" src="https://github.com/user-attachments/assets/d183f45a-75c0-44e8-baba-80c3806cde3d" />

      code :
              .venv\Scripts\activate

    -->  on mac/linux ,
          <img width="652" height="117" alt="image" src="https://github.com/user-attachments/assets/2efd44c8-4eec-4da6-bac5-2593cf825b0c" />

      code :
               source .venv/bin/activate


    Install the Required Libraries:
    
     All project dependencies are listed in requirements.txt.

    <img width="689" height="119" alt="image" src="https://github.com/user-attachments/assets/f2fc902b-dd12-4cda-b6e6-a15165fded41" />


    code :
            pip install -r requirements.txt


    Setting Up Environment Variables

    This project uses an environment variable to securely connect to your MongoDB database.

    Create a file named .env in the root of your project.

    Add your MongoDB Atlas connection string to the file using the key MONGO_URI.

    <img width="696" height="85" alt="image" src="https://github.com/user-attachments/assets/a593112b-e3b0-431d-8ff8-dd59e6c81e3d" />

    Note: Replace <username>, <password>, <cluster-name>, and <app-name> with your actual MongoDB credentials. Do not hardcode these values directly into your code.



    Running the Project :-
    
       Once you have completed the setup, you can run the application with Uvicorn.

       <img width="724" height="112" alt="image" src="https://github.com/user-attachments/assets/e7ca0861-02bf-41fd-82b6-5fb28f0e3f5b" />

       code :
               uvicorn main:app --reload


        API will be running at http://127.0.0.1:8000  and  such an interface can be seen .


      <img width="800" height="77" alt="image" src="https://github.com/user-attachments/assets/23e1ae05-d790-4a6a-a7bc-dca5b1b09dc1" />


      Note : As  this service is hosted , i will be now sharing  the hosted link  and interfaces of testing each  end point .

      The hosted link :

       https://url-shortner-web-service.onrender.com/


     The interface will look like this :
        


       





     


    


          



