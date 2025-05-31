# Blockchain-based E-voting System with Facial Recognition

This project implements a secure electronic voting platform leveraging blockchain technology and facial recognition for voter authentication. The system aims to provide transparent, tamper-proof, and user-friendly online voting, ensuring only authorized individuals can vote while maintaining voter privacy and election integrity.

## Features

- **Blockchain-Backed Voting:** Votes are stored on a blockchain, providing immutability and transparency.
- **Facial Recognition Authentication:** Uses facial recognition to authenticate voters, preventing impersonation and duplicate voting.
- **Decentralized and Secure:** Protects against vote tampering and unauthorized access.
- **User-Friendly Interface:** Simple web interface for voters and administrators.
- **Admin Controls:** Manage elections, candidates, and monitor voting activity.
- **Auditability:** All actions are logged for traceability and post-election audits.

## Technology Stack

- **Backend:** Python (Django)
- **Frontend:** JavaScript (React Native)
- **Smart Contracts:** Solidity (Ethereum-compatible blockchain)
- **Facial Recognition:** OpenCV, deepface (Python libraries)
- **Database:** SQLite
- **Web3 Integration:** Web3.py

## Directory Structure

```
.
├── backend/               # Flask backend, facial recognition, blockchain logic
├── contracts/             # Solidity smart contracts
├── frontend/              # Web UI for voters and admins
├── requirements.txt       # Python dependencies
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.7+
- Node.js & npm (for frontend)
- Ganache 
- pipenv or virtualenv (recommended)
- deepface https://github.com/serengil/deepface Python library

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ZenonWrites/Blockchain-based-E-voting-system-with-Facial-recognition.git
   cd Blockchain-based-E-voting-system-with-Facial-recognition
   ```

2. **Set up the backend:**

   ```bash
   cd backend
   python -m venv myenv
   .\myenv\Scripts\Activate
   pip install -r requirements.txt
   # Configure .env for secrets, blockchain endpoint, etc.
   python manage.py runserver
   ```

3. **Deploy smart contracts:**
   Open a new terminal 
   ```bash
   npx ganache (Your Ip address)
   # Using Truffle, deploy contracts to your blockchain while the ganache terminal is still running
   cd backend
   truffle migrate
   ```

4. **Run the frontend:**

   ```bash
   cd ../frontend
   npx expo install
   npx expo start
   ```

### Facial Recognition Setup

- Enroll voters by capturing their facial data via the frontend or an admin tool.
- Facial images are processed and compared at vote time to confirm identity.

## Usage

1. **Register Voters:** Admin enrolls voters with facial data.
2. **Start Election:** Admin creates and starts a new election.
3. **Authenticate & Vote:** Voters log in, complete facial recognition, and cast their vote.
4. **View Results:** Results can be viewed in real-time and are verifiable on the blockchain.

## Security & Privacy

- Facial images are used for verification only and are not stored without encryption.
- Each vote is recorded as a transaction on the blockchain, making it tamper-evident.
- Only authorized voters may cast a single vote.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [OpenCV](https://opencv.org/)
- [face_recognition][(https://github.com/serengil/deepface)]
- [Ethereum](https://ethereum.org/)
- [web3.py](https://github.com/ethereum/web3.py)

---

*For demo and research purposes only. Not intended for use in official government elections.*
