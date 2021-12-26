import flask
from flask import request
import json
from pathlib import Path


# Load a high score list from file. If no file exists, create it using defaults
def load_high_score_file(filename_base, version, level):
    full_file_name = f"{filename_base}_{version}_{level}.json"
    file_name_path = Path(full_file_name)
    if file_name_path.is_file():
        with open(full_file_name, 'r') as file:
            return json.load(file)
    else:
        default_high_score = create_default_score()
        # default_high_score_list = json.dumps(default_high_score)
        save_high_score_file(filename_base, version, level, default_high_score)
        return load_high_score_file(filename_base, version, level)


# Save the high score list to a file
def save_high_score_file(filename_base, version, level, list_to_save):
    full_file_name = f"{filename_base}_{version}_{level}.json"
    with open(full_file_name, 'w') as file:
        json.dump(list_to_save, file)


# Create a set of default scores
def create_default_score():
    default_high_score_list = [
        {'name': 'Emily', 'score': 5000.0},
        {'name': 'Callum', 'score': 4000.0},
        {'name': 'Debbie', 'score': 3000.0},
        {'name': 'Oli', 'score': 2000.0},
        {'name': 'PJ', 'score': 1000.0}
    ]
    return default_high_score_list


# Returns the top 'n' records, ordered by score
def keep_top_scores(num_to_keep, scores_list):
    # Sort the list
    sorted_list = sorted(scores_list, key=lambda dic: dic['score'], reverse=True)

    # Return the top n
    return sorted_list[:num_to_keep]


# Run the flask server process
def run_server(filename_base):

    app = flask.Flask(__name__)
    app.config["DEBUG"] = True

    # This is the 'get' method, which returns the high score list for the given version and level
    @app.route('/get', methods=['GET'])
    def get_scores():
        version = request.args.get('version')
        level = request.args.get('level')
        print(f"GET Request received: Version: {version}, Level: {level}")
        high_score_list = load_high_score_file(filename_base, version, level)
        json_response = flask.jsonify(high_score_list)
        return json_response

    # This is the 'submit' method, that consumes a score and updates the high score table, if appropriate
    @app.route('/submit', methods=['POST'])
    def submit_score():

        # Get values from request
        version = request.args.get('version')
        level = request.args.get('level')
        name = request.args.get('name')
        score = float(request.args.get('score'))

        print(f"SUBMIT request received: Version: {version}, Level: {level}, Name: {name}, Score: {score}")

        # Load the list
        high_score_list = load_high_score_file(filename_base, version, level)

        # Add the new score onto the list
        high_score_list.append({'name': name, 'score': score})

        # Recalculate  and return top 5
        top_scores_list = keep_top_scores(5, high_score_list)

        # Write back to the file
        save_high_score_file(filename_base, version, level, top_scores_list)

        # Was this a new high score entry?
        new_high_score = {'name': name, 'score': score} in top_scores_list

        # Return success
        return json.dumps([
            {'success': True}, {'new_high_score': new_high_score}
        ]), 200, {'ContentType': 'application/json'}

    # app.run("192.248.173.228")
    app.run()


# Run the main Flask server
if __name__ == '__main__':
    run_server(".\\hide_high_scores")
