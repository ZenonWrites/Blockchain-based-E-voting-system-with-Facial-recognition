const VotingContract = artifacts.require("VotingContract");

module.exports = function (deployer) {
  deployer.deploy(VotingContract);
};