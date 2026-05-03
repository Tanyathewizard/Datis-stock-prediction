// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * DATIS Prediction Registry
 * Stores AI stock predictions on-chain for transparency and auditability.
 * Compatible with Ethereum testnets (Sepolia, Goerli) and local Hardhat/Ganache.
 */
contract DatisPredictions {

    // ─── Structs ────────────────────────────────────────────────────────────

    struct Prediction {
        uint256 tokenId;
        string  symbol;          // e.g. "AAPL"
        string  prediction;      // "BUY" | "SELL" | "HOLD"
        uint8   confidence;      // 0–100
        uint256 timestamp;       // block.timestamp at storage time
        int256  priceAtPrediction; // price * 100 to avoid floats (e.g. 18250 = $182.50)
        string  actualResult;    // filled in later: "CORRECT" | "INCORRECT" | "PENDING"
        int256  priceAtResolution;
        bool    resolved;
        address submitter;       // wallet that stored this prediction
    }

    // ─── State ──────────────────────────────────────────────────────────────

    uint256 private _nextTokenId;
    mapping(uint256 => Prediction) private _predictions;
    mapping(string  => uint256[])  private _symbolIndex;  // symbol → list of tokenIds
    address public owner;

    // ─── Events ─────────────────────────────────────────────────────────────

    event PredictionStored(
        uint256 indexed tokenId,
        string  indexed symbol,
        string  prediction,
        uint8   confidence,
        uint256 timestamp
    );

    event ResultUpdated(
        uint256 indexed tokenId,
        string  actualResult,
        int256  priceAtResolution
    );

    // ─── Modifiers ──────────────────────────────────────────────────────────

    modifier onlyOwner() {
        require(msg.sender == owner, "DatisPredictions: caller is not owner");
        _;
    }

    modifier tokenExists(uint256 tokenId) {
        require(tokenId < _nextTokenId, "DatisPredictions: token does not exist");
        _;
    }

    // ─── Constructor ────────────────────────────────────────────────────────

    constructor() {
        owner = msg.sender;
        _nextTokenId = 0;
    }

    // ─── Write Functions ────────────────────────────────────────────────────

    /**
     * @notice Store a new AI prediction. Returns the new token id.
     * @param symbol           Ticker symbol (e.g. "AAPL")
     * @param prediction       Decision string: "BUY", "SELL", or "HOLD"
     * @param confidence       Confidence percentage 0–100
     * @param priceAtPrediction Current price multiplied by 100 (avoids decimals)
     */
    function storePrediction(
        string  calldata symbol,
        string  calldata prediction,
        uint8            confidence,
        int256           priceAtPrediction
    ) external returns (uint256) {
        require(bytes(symbol).length > 0,     "DatisPredictions: symbol required");
        require(bytes(prediction).length > 0, "DatisPredictions: prediction required");
        require(confidence <= 100,            "DatisPredictions: confidence must be 0-100");

        uint256 tokenId = _nextTokenId;
        _nextTokenId++;

        _predictions[tokenId] = Prediction({
            tokenId:            tokenId,
            symbol:             symbol,
            prediction:         prediction,
            confidence:         confidence,
            timestamp:          block.timestamp,
            priceAtPrediction:  priceAtPrediction,
            actualResult:       "PENDING",
            priceAtResolution:  0,
            resolved:           false,
            submitter:          msg.sender
        });

        _symbolIndex[symbol].push(tokenId);

        emit PredictionStored(tokenId, symbol, prediction, confidence, block.timestamp);
        return tokenId;
    }

    /**
     * @notice Update the actual outcome of a prediction (owner only).
     * @param tokenId           The token to update
     * @param actualResult      "CORRECT" or "INCORRECT"
     * @param priceAtResolution Closing/resolution price * 100
     */
    function updateActualResult(
        uint256         tokenId,
        string calldata actualResult,
        int256          priceAtResolution
    ) external onlyOwner tokenExists(tokenId) {
        require(!_predictions[tokenId].resolved, "DatisPredictions: already resolved");

        _predictions[tokenId].actualResult      = actualResult;
        _predictions[tokenId].priceAtResolution = priceAtResolution;
        _predictions[tokenId].resolved          = true;

        emit ResultUpdated(tokenId, actualResult, priceAtResolution);
    }

    // ─── Read Functions ─────────────────────────────────────────────────────

    /**
     * @notice Fetch a single prediction by token id.
     */
    function getPrediction(uint256 tokenId)
        external
        view
        tokenExists(tokenId)
        returns (Prediction memory)
    {
        return _predictions[tokenId];
    }

    /**
     * @notice Return all token ids for a given symbol.
     */
    function getTokensBySymbol(string calldata symbol)
        external
        view
        returns (uint256[] memory)
    {
        return _symbolIndex[symbol];
    }

    /**
     * @notice Total number of predictions stored.
     */
    function totalPredictions() external view returns (uint256) {
        return _nextTokenId;
    }

    /**
     * @notice Transfer contract ownership.
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "DatisPredictions: zero address");
        owner = newOwner;
    }
}
