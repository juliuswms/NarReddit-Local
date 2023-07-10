import requests
import json
from datetime import timedelta


class ForcedAligner:
    def __init__(self, gentleUrl, env):
        self.gentleUrl = gentleUrl
        self.env = env

    def align(self, audioPath, transcription, srtOutputPath):
        # Open the audio file
        with open(audioPath, 'rb') as audioFile:
            # Send a POST request to the Gentle API
            response = requests.post(
                f'{self.gentleUrl}/transcriptions?async=false',
                data={'transcript': transcription},
                files={'audio': audioFile}
            )

        # Check the status code of the response
        if response.status_code != 200:
            print(
                f"Error: received status code {response.status_code} from Gentle")
            return

        # Parse the alignment results
        alignment = json.loads(response.text)

        # Convert the alignment to SRT format and save it to the output file
        with open(srtOutputPath, 'w') as srtFile:
            srtIndex = 1
            phrase = []
            phraseCharCount = 0
            for word in alignment['words']:
                if word['case'] != 'success':
                    continue

                wordLen = len(word['alignedWord'])
                if phraseCharCount + wordLen <= 15:
                    phrase.append(word)
                    phraseCharCount += wordLen
                else:
                    self.writeSrtCue(srtFile, srtIndex, phrase)
                    srtIndex += 1
                    phrase = [word]
                    phraseCharCount = wordLen

            # Write the final phrase, if any
            if phrase:
                self.writeSrtCue(srtFile, srtIndex, phrase)

    def writeSrtCue(self, srtFile, index, phrase):
        startTime = timedelta(seconds=phrase[0]['start'])
        endTime = timedelta(seconds=phrase[-1]['end'])
        words = [word['alignedWord'] for word in phrase]
        srtFile.write(f"{index}\n")
        srtFile.write(f"{startTime} --> {endTime}\n")
        srtFile.write(' '.join(words) + "\n\n")
