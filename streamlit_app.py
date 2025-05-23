# Import python packages
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(f"🥤Customize Your Smoothie!🥤")
st.write(
  """Choose the fruits you want in your custom Smoothie!
  """
)

name_on_order = st.text_input('Name on Smoothie:')
st.write('the name on your smoothie will be: ',name_on_order)

# session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

#Convert the snowpark Dataframe to a pandas dataframe so we can use the LOC function
pd_df = my_dataframe.to_pandas()
# st.dataframe(pd_df)
# st.stop()


ingredient_list = st.multiselect(
    'choose upto 5 ingredients: '
    , my_dataframe
    , max_selections=5
)

if ingredient_list:
    # st.write(ingredient_list)
    # st.text(ingredient_list)

    ingredients_string = ''

    for fruit in ingredient_list:
        ingredients_string += fruit + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit, ' is ', search_on,'.')
      
        st.subheader(fruit + ' Nutrition Information')
        if search_on:
          smoothiefroot_resposnse = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on)
          sf_df = st.dataframe(data=smoothiefroot_resposnse.json(), use_container_width = True)
        else:
          smoothiefroot_resposnse = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit)
          sf_df = st.dataframe(data=smoothiefroot_resposnse.json(), use_container_width = True)
        
    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string +"""','""" +name_on_order+"""');"""

    # st.write(my_insert_stmt)
    # st.stop()
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f"✅ Your Smoothie is ordered, {name_on_order}!")


#New section to display smoothiefroot nutrition information
# st.text(smoothiefroot_resposnse.json())

