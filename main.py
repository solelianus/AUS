import requests, json
from bs4 import BeautifulSoup
import sqlite3


# ONLY EDIT THIS
search_query = "Undergraduate"
page_numbers = 2


def extract_links(query="Undergraduate",page_number=1):
    search_url = f"https://search.studyaustralia.gov.au/courses?level_of_study=undergraduate&page={page_number}&query={query}"
    r = requests.get(search_url)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all(
            "a",
            {
                "role": "link",
                "target": "_self",
                "class": "inline-block transition duration-150 bg-transparent text-center text-primary font-au-sans-medium border-0 rounded-3xl py-2 px-4 hover:underline hover:text-austrade no-underline w-full md:w-fit",
            },
            href=True,
        )
    course_links = []
    for link in links:
        full_url = "https://search.studyaustralia.gov.au" + link["href"]
        course_links.append(full_url)
    return course_links

def extract_info(url="https://search.studyaustralia.gov.au/course/associate-degree-of-engineering/d572f5ae0d48176138a53d5c0619b5a2"):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    app = soup.find("div", id="app")
    # Extract JSON data from the data-page attribute
    try:
        data = json.loads(app['data-page'])
    except json.JSONDecodeError:
        print("Failed to parse JSON data.")
        return
    course_name = data.get('props', {}).get('course', {}).get('name','N/A')
    collage_name = data.get('props', {}).get('course', {}).get('organisation', {}).get('name', 'N/A')
    course_data = data.get('props', {}).get('course', {}).get('sites', [{}])[0]
    cricos_code = course_data.get('cricos_code', 'N/A')
    start_date = course_data.get('course_start_date','N/A')
    address = f"{course_data.get('name', 'N/A')}, {course_data.get('street1', 'N/A')},{course_data.get('state_name_full','N/A')} {course_data.get('postcode','N/A')}"
    # Safe access to the 'attendance' list
    attendance_data = course_data.get('attendance', [])
    if attendance_data:
        attendance_data = attendance_data[0]
    else:
        attendance_data = {}  # Handle the case where the list is empty
    attendance_options = f"{attendance_data.get('name', 'N/A')} - {attendance_data.get('length', 'N/A')} years" \
        if attendance_data.get('name') and attendance_data.get('length') else 'N/A'
    total_tuition_costs = course_data.get('fees', {}).get('overseas_full_fee', 'N/A')


    return {
        "course_name" : course_name,
        "collage_name": collage_name,
        "cricos_code" : cricos_code,
        "start_date" : start_date,
        "address" : address,
        "attendance_options" : attendance_options,
        "total_tuition_costs" : f'${total_tuition_costs} AUD',
    }




def main():
    global search_query, page_numbers  # Access global variables
    
    # Initialize SQLite database
    conn = sqlite3.connect("course_data.db")
    c = conn.cursor()

    # Create the course table if it doesn't already exist
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS course (
            id INTEGER PRIMARY KEY,
            name TEXT,
            college TEXT,
            cricos_code TEXT,
            start_date TEXT,
            address TEXT,
            attendance_options TEXT,
            tuition_costs TEXT
        )
        """
    )

    for page_number in range(1, page_numbers + 1):  # Loop through specified page numbers
        # Fetch course links from the current page
        links = extract_links(search_query, page_number)
        if not links:  # Break the loop if no more links are found
            break

        for link in links:
            try:                
                # Extract course details for each link
                course_info = extract_info(link)
                # Insert the extracted details into the database
                c.execute(
                    """
                    INSERT INTO course (
                        name, college, cricos_code, start_date, address, attendance_options, tuition_costs
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        course_info["course_name"],
                        course_info["collage_name"],
                        course_info["cricos_code"],
                        course_info["start_date"],
                        course_info["address"],
                        course_info["attendance_options"],
                        course_info["total_tuition_costs"],
                    ),
                )
                print(f"Inserted: {course_info['course_name']}")  # Log success
            except Exception as e:
                print(f"Error processing {link}: {e}")  # Log errors

    # Commit the changes and close the database connection
    conn.commit()
    conn.close()
    print("All courses have been processed and saved to the database.")

if __name__ == "__main__":
    main()