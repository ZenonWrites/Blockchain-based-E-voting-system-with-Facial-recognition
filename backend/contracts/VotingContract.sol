// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract VotingContract {
    mapping(address => uint256) public votes;
    mapping(uint256 => uint256) public candidateVotes;
    uint256[] public candidates;
    bool public votingOpen;

    event VoteCast(address voter, uint256 candidate);
    event VotingStatusChanged(bool open);

    constructor() {
        votingOpen = false;
    }

    function addCandidate(uint256 _candidate) public {
        require(!votingOpen, "Voting is already open");
        candidates.push(_candidate);
    }

    function openVoting() public {
        require(!votingOpen, "Voting is already open");
        votingOpen = true;
        emit VotingStatusChanged(true);
    }

    function closeVoting() public {
        require(votingOpen, "Voting is already closed");
        votingOpen = false;
        emit VotingStatusChanged(false);
    }

    function vote(uint256 _candidate) public {
        require(votingOpen, "Voting is not open");
        require(votes[msg.sender] == 0, "Voter has already voted");

        candidateVotes[_candidate]++;
        votes[msg.sender] = _candidate;
        emit VoteCast(msg.sender, _candidate);
    }

    function getWinner() public view returns (uint256) {
        require(!votingOpen, "Voting is still open");

        uint256 winner = 0;
        uint256 maxVotes = 0;

        for (uint256 i = 0; i < candidates.length; i++) {
            if (candidateVotes[candidates[i]] > maxVotes) {
                maxVotes = candidateVotes[candidates[i]];
                winner = candidates[i];
            }
        }

        return winner;
    }
}
