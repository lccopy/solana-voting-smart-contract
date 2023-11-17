const Voting = artifacts.require("Voting");

contract("Voting", function(accounts) {
    let votingInstance;

    beforeEach(async function() {
      votingInstance = await Voting.new();
    });

    it("initializes with two candidates", async function() {
        const count = await votingInstance.candidatesCount();
        assert.equal(count, 2);
    });

    it("allows a voter to cast a vote", async function() {
        const candidateId = 1;
        await votingInstance.vote(candidateId, { from: accounts[0] });
        const candidate = await votingInstance.candidates(candidateId);
        assert.equal(candidate.voteCount, 1, "accepts first vote");
    });

    it("throws an exception for invalid candidates", async function() {
        try {
            await votingInstance.vote(99, { from: accounts[1] });
            assert.fail();
        } catch (error) {
            assert(error.toString().includes("revert Invalid candidate."), "expected throw but got: " + error.toString());
        }
    });

    it("throws an exception for double voting", async function() {
        const candidateId = 2;
        await votingInstance.vote(candidateId, { from: accounts[2] });
        const candidate = await votingInstance.candidates(candidateId);
        assert.equal(candidate.voteCount, 1, "accepts first vote");

        try {
            await votingInstance.vote(candidateId, { from: accounts[2] });
            assert.fail();
        } catch (error) {
            assert(error.toString().includes("revert Voter has already voted."), "expected throw but got: " + error.toString());
        }
    });

    it("allows a voter to vote for candidate 1", async function() {
      const candidate1Id = 1;
      await votingInstance.vote(candidate1Id, { from: accounts[3] });
      const candidate1 = await votingInstance.candidates(candidate1Id);
      assert.equal(candidate1.voteCount, 1, "accepts first vote for candidate 1");
    });

      it("allows a voter to vote for candidate 2", async function() {
        const candidate2Id = 2;
        await votingInstance.vote(candidate2Id, { from: accounts[4] });
        const candidate2 = await votingInstance.candidates(candidate2Id);
        assert.equal(candidate2.voteCount, 1, "accepts first vote for candidate 2");
    });

    it("initializes candidates with the correct values", async function() {
      const candidate1 = await votingInstance.candidates(1);
      assert.equal(candidate1.name, "Candidat 1", "Candidate 1 name is correct");
      assert.equal(candidate1.voteCount, 0, "Candidate 1 initial vote count is correct");

      const candidate2 = await votingInstance.candidates(2);
      assert.equal(candidate2.name, "Candidat 2", "Candidate 2 name is correct");
      assert.equal(candidate2.voteCount, 0, "Candidate 2 initial vote count is correct");
    });

    it("emits a votedEvent when a vote is cast", async function() {
        const candidateId = 1;
        const result = await votingInstance.vote(candidateId, { from: accounts[5] });
        assert.equal(result.logs[0].event, "votedEvent", "votedEvent is emitted");
        assert.equal(result.logs[0].args._candidateId.toNumber(), candidateId, "Candidate ID is correct");
    });

});
