package main

import (
	"bytes"
	"context"
	"database/sql"
	"io/ioutil"
    "sync"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"
	// "strconv"
	// "io"
	"encoding/json"
	"github.com/gin-gonic/gin"
	// "database/sql"
	// "encoding/json"
	"fmt"
	"github.com/confluentinc/confluent-kafka-go/kafka"
	_ "github.com/godror/godror"
	_ "github.com/lib/pq"
)

const (
	DruidUrl       = "http://172.31.18.187:8082"
	NegListApi     = "https://nlm.easebuzz.dev/api/v1/nlist/check"
	StatusNotFound = 404
	dbHost         = "breaking-code-1.cjisqek2oox2.ap-south-1.rds.amazonaws.com"
	dbPort         = "5432"
	dbUser         = "postgres"
	dbPassword     = "your_password_here" // Replace with your actual password
	dbName         = "breaking_code"
	sslMode        = "disable"
	KafkaServer    = "13.202.202.210:9092"
	EbzTxnsTopic   = "EbzTxnsTopic"
)

var db *sql.DB
var prod *kafka.Producer
type APIResponse struct {
    RuleID  int             // To identify which rule this response belongs to
    Data    string // Adjust based on the expected response
}

type RuleResult struct {
    IsGreaterThanLookup bool `json:"is_greater_than_lookup"`
    // Add other fields if necessary
}

func dbinit() {
	// Database connection constants
	const (
		dbHost     = "breaking-code-1.cjisqek2oox2.ap-south-1.rds.amazonaws.com"
		dbPort     = "5432"
		dbUser     = "postgres"
		dbPassword = "Root#123"
		dbName     = "breaking_code"
		sslMode    = "require"
	)

	// Build the connection string
	connStr := fmt.Sprintf(
		"host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		dbHost, dbPort, dbUser, dbPassword, dbName, sslMode,
	)

	var err error
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal("Error connecting to the database:", err)
	}

	// Set database connection pool settings
	db.SetMaxOpenConns(25)
	db.SetMaxIdleConns(25)
	db.SetConnMaxLifetime(time.Hour)
}

// TransactionRule represents a row in the transaction_rules table
type TransactionRule struct {
	RuleID          int            `json:"rule_id"`
	MerchantID      sql.NullInt32  `json:"merchant_id"`
	SQLQuery        sql.NullString `json:"sql_query"`
	RuleScore       sql.NullInt32  `json:"rule_score"`
	RuleDescription sql.NullString `json:"rule_description"`
	RuleTitle       sql.NullString `json:"rule_title"`
	FraudEntity     sql.NullString `json:"fraud_entity"`
	FraudType       string         `json:"fraud_type"`
}

type Transaction struct {
	AccountNumber string  `json:"account_number"`
	VPA           string  `json:"vpa"`
	OriginIP      string  `json:"origin_ip"`
	MCC           string  `json:"mcc"`
	Mode          string  `json:"mode"`
	TxnsID        int     `json:"txns_id"`
	MerchantID    int     `json:"merchant_id"`
	Amount        float64 `json:"amount"`
	Narration     string  `json:"narration"`
	DeviceId      string  `json:"device_id"`
	Pincode       string  `json:"pin_code"`
}

func LoggerMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		log.Println("Request started")
		c.Next()
		log.Println("Request finished")
	}
}

// Define a basic health check route
func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message": "Server is up and running!",
	})
}

// Struct to hold the combined response
type CombinedResponse struct {
	RuleCheckResponse string `json:"api1_response"`
	AccRes       string `json:"account"`
	IpRes        string `json:"ip"`
	DeviceRes    string `json:"deviceRes"`
	PincodeRes   string `json:"pincodeRes"`
	// DruidResult  interface{} `json:"druid_result"`
	Error  string `json:"errororempty"`
	STATUS string `json:"TxnsStatus"`
}

func ruleCheckApi(rule TransactionRule) string{
	// func ruleCheckApi(resultChan chan<- string, errChan chan<- error) {

	url := DruidUrl + "/druid/v2/sql"
	// jsonData := `{
	// 	"query": "SELECT COUNT(*) AS total_count FROM T1"
	// }`
	// jsonData := `{
	// 	"query": """SELECT CASE WHEN COALESCE(sum(amount), 0) > CAST(LOOKUP('-1', 'GMVLookupTable') AS DOUBLE) THEN TRUE ELSE FALSE END AS is_greater_than_lookup FROM "EbzTxnsTopic" where  TIMESTAMP_TO_MILLIS("__time") >= (TIMESTAMP_TO_MILLIS(CURRENT_TIMESTAMP) - CAST(LOOKUP('-1', 'shortTimePeriodLookupTable') AS BIGINT)*1000) AND "merchant_id" = 9999"""
	// }`
	// query := `SELECT CASE WHEN COALESCE(sum(amount), 0) > CAST(LOOKUP('-1', 'GMVLookupTable') AS DOUBLE)
	// THEN TRUE ELSE FALSE END AS is_greater_than_lookup
	// FROM "EbzTxnsTopic"
	// WHERE TIMESTAMP_TO_MILLIS("__time") >= (TIMESTAMP_TO_MILLIS(CURRENT_TIMESTAMP) - CAST(LOOKUP('-1', 'shortTimePeriodLookupTable') AS BIGINT)*1000)
	// AND "merchant_id" = 9999`

	data := map[string]string{
		// "query": query,
		"query": rule.SQLQuery.String,
	}

	jsonDataBytes, err := json.Marshal(data)
	if err != nil {
		log.Fatalf("Error marshaling JSON: %v", err)
	}
	// Create a new POST request
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonDataBytes))
	// req, err := http.NewRequest("POST", url, bytes.NewBuffer([]byte(jsonData)))

	if err != nil {
		// errChan <- err
		return err.Error() 
	}

	// Set the headers
	req.Header.Set("Content-Type", "application/json")

	// Perform the request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		// fmt.Println("Error sending request:", err)
		return err.Error() 
	}
	defer resp.Body.Close()

	// Read the response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return err.Error() 
	}

	return string(body)
}

// Function to call external API 2 concurrently
func negListApi(resultChan chan<- string, errChan chan<- error, data map[string]string) {
	url := NegListApi

	// Marshal the map into JSON
	jsonData, err := json.Marshal(data)
	if err != nil {
		errChan <- err

		// fmt.Println("Error marshalling JSON:", err)
		return
	}

	// // JSON data for the POST request
	// jsonData := `{
	// 	"query": "SELECT COUNT(*) AS total_count FROM T1"
	// }`

	// Create a new POST request
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))

	if err != nil {
		errChan <- err
		return
	}

	// Set the headers
	req.Header.Set("Content-Type", "application/json")

	// Perform the request
	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Println("Error sending request:", err)
		return
	}
	defer resp.Body.Close()

	// Read the response body
	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Error reading response:", err)
		return
	}
	resultChan <- string(body)
}

func getTransactionRules(c *gin.Context, specificMerchantID int) []TransactionRule {

	var transactionRules []TransactionRule
	query := `
        SELECT 
            rule_id, merchant_id, sql_query, rule_score, 
            rule_description, rule_title, fraud_entity, fraud_type
        FROM transaction_rules where merchant_id = -1 OR merchant_id = $1;
    `

	// ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	ctx, cancel := context.WithTimeout(c.Request.Context(), 5*time.Second)
	defer cancel()

	rows, err := db.QueryContext(ctx, query, specificMerchantID)
	if err != nil {
		log.Println("Error executing query:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database query failed"})
		return transactionRules
	}
	defer rows.Close()

	// Iterate over the rows
	for rows.Next() {
		var rule TransactionRule

		err := rows.Scan(
			&rule.RuleID,
			&rule.MerchantID,
			&rule.SQLQuery,
			&rule.RuleScore,
			&rule.RuleDescription,
			&rule.RuleTitle,
			&rule.FraudEntity,
			&rule.FraudType,
		)
		if err != nil {
			log.Println("Error scanning row:", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading data"})
			return transactionRules
		}

		transactionRules = append(transactionRules, rule)
	}

	// Check for any errors encountered during iteration
	if err := rows.Err(); err != nil {
		log.Println("Error during row iteration:", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading data"})
		return transactionRules
	}
	return transactionRules

}
func updateFraudRules(txn Transaction, rulesBrokenData []byte) {
	query := `
    INSERT INTO fraud_transaction_data (
        account_number,
        vpa,
        origin_ip,
        mcc,
        mode,
        txns_id,
        merchant_id,
        amount,
        narration,
        device_id,
        pin_code,
        rules_broken
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12
    ) RETURNING id
    `
	var lastInsertID int
    err := db.QueryRow(
        query,
        txn.AccountNumber,
        txn.VPA,
        txn.OriginIP,
        txn.MCC,
        txn.Mode,
        txn.TxnsID,
        txn.MerchantID,
        txn.Amount,
        txn.Narration,
        txn.DeviceId,
        txn.Pincode,
        rulesBrokenData,
    ).Scan(&lastInsertID)
	if err != nil {
        log.Fatalf("Error inserting data into database: %v", err)
    }

    fmt.Printf("Data inserted successfully with ID %d\n", lastInsertID)
}

func handleConcurrentRequests(c *gin.Context) {
	errChan := make(chan error)
	// Define the number of channels you need
	const numNegList = 5

	// Create an array of channels
	var negChan [numNegList]chan string
	// Initialize each channel in the array
	for i := 0; i < numNegList; i++ {
		negChan[i] = make(chan string)
	}
	var txn Transaction
	// Bind the JSON payload to the struct
	if err := c.ShouldBindJSON(&txn); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error":   "Invalid request payload",
			"details": err.Error(),
		})
		return
	}

	transactionRules := getTransactionRules(c, txn.MerchantID)
	// Call external APIs and Druid SQL concurrently using goroutines
	if transactionRules == nil {
		return
	}

	responseChan := make(chan APIResponse, len(transactionRules))

	// WaitGroup to wait for all goroutines to finish
	var wg sync.WaitGroup

	// Iterate over the transactionRules slice
	for _, rule := range transactionRules {
		wg.Add(1)
		// Create a local copy of the rule to avoid variable capture issues
		rule := rule

		go func() {
			defer wg.Done()

			// Make the API request
			apiResponse := ruleCheckApi(rule)
			

			// Send the response back through the channel
			responseChan <- APIResponse{
				RuleID: rule.RuleID,
				Data:   apiResponse,
			}
		}()
	}

	
	
	acc_no := map[string]string{
		"article_type": "acc_no",
		"article":      txn.AccountNumber,
	}
	go negListApi(negChan[0], errChan, acc_no)
	
	device := map[string]string{
		"article_type": "device",
		"article":      txn.DeviceId,
	}
	go negListApi(negChan[1], errChan, device)
	
	ip := map[string]string{
		"article_type": "ip",
		"article":      txn.OriginIP,
	}
	go negListApi(negChan[2], errChan, ip)
	
	pin_code := map[string]string{
		"article_type": "pin_code",
		"article":      txn.Pincode,
	}
	go negListApi(negChan[3], errChan, pin_code)
	
	var  accRes, deviceRes, pincodeRes, ipRes string
	// var druidResult interface{}
	var apiError string
	
	// Wait for all goroutines to finish
	go func() {
		wg.Wait()
		close(responseChan)
	}()

	// Collect and process responses
	var fraudResponses []APIResponse
	enableFlag := false
	for resp := range responseChan {

		var results []RuleResult
		err := json.Unmarshal([]byte(resp.Data), &results)
		if err != nil {
			log.Printf("Error parsing JSON for RuleID %d: %v", resp.RuleID, err)
			continue
		}
		// fmt.Print("results: ",results)
		for _, result := range results {
			if result.IsGreaterThanLookup {
				enableFlag = true
				fraudResponses = append(fraudResponses, resp)
			}
		}
	}


	// Wait for responses from all channels, including errors
	for i := 0; i < 4; i++ {
		select {
		case acc := <-negChan[0]:
			var dataMap map[string]bool
			// Unmarshal the JSON string into the map
			err := json.Unmarshal([]byte(acc), &dataMap)
			if err != nil {
				log.Fatalf("Error unmarshaling JSON: %v", err)
			}

			// Print the map for verification
			
			// Initialize the flag
			
			// Check if both values are true
			if dataMap["in_negative_list"] || dataMap["is_temp_blocked"] {
				enableFlag = true
			}
			accRes = acc
		case device := <-negChan[1]:
			var dataMap map[string]bool
			// Unmarshal the JSON string into the map
			err := json.Unmarshal([]byte(device), &dataMap)
			if err != nil {
				log.Fatalf("Error unmarshaling JSON: %v", err)
			}
			
			// Check if both values are true
			if dataMap["in_negative_list"] || dataMap["is_temp_blocked"] {
				enableFlag = true
			}
			deviceRes = device
		case ip := <-negChan[2]:
			var dataMap map[string]bool
			// Unmarshal the JSON string into the map
			err := json.Unmarshal([]byte(ip), &dataMap)
			if err != nil {
				log.Fatalf("Error unmarshaling JSON: %v", err)
			}
			// Check if both values are true
			if dataMap["in_negative_list"] || dataMap["is_temp_blocked"] {
				enableFlag = true
			}
			ipRes = ip
		case pincode := <-negChan[3]:
			var dataMap map[string]bool
			// Unmarshal the JSON string into the map
			err := json.Unmarshal([]byte(pincode), &dataMap)
			if err != nil {
				log.Fatalf("Error unmarshaling JSON: %v", err)
			}
			// Check if both values are true
			if dataMap["in_negative_list"] || dataMap["is_temp_blocked"] {
				enableFlag = true
			}
			pincodeRes = pincode
		// case druidResp := <-druidChan:
		// 	druidResult = druidResp
		case err := <-errChan:
			apiError = err.Error()
		}
	}

	jsonData, err := json.Marshal(fraudResponses)
	if err != nil {
		log.Fatalf("Error marshaling fraudResponses to JSON: %v", err)
	}

	// Convert the JSON data to a string
	jsonString := string(jsonData)
	// Combine the results into a single response
	response := CombinedResponse{
		RuleCheckResponse: jsonString,
		AccRes:       accRes,
		IpRes:        ipRes,
		DeviceRes:    deviceRes,
		PincodeRes:   pincodeRes,
		// DruidResult:  druidResult,
		Error:  apiError,
		STATUS: "success",
	}
	
	rulesBrokenData, err := json.Marshal(response)
	if err != nil {
		log.Fatalf("Error marshaling CombinedResponse to JSON: %v", err)
	}
	if enableFlag{
		updateFraudRules(txn, rulesBrokenData)
	}
	produceTrascation(txn)
	// Send the combined response back to the client
	c.JSON(http.StatusOK, response)
}

func main() {

	dbinit()
	var err error
	router := gin.Default()
	router.Use(LoggerMiddleware())
	router.GET("/health", healthCheck)
	router.POST("/rulechecker", handleConcurrentRequests)

	prod, err = kafka.NewProducer(&kafka.ConfigMap{
		"bootstrap.servers": KafkaServer,
	})
	if err != nil {
		panic(err)
	}
	defer prod.Close()

	srv := &http.Server{
		Addr:    ":8080",
		Handler: router,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			log.Fatalf("listen: %s\n", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	log.Println("Shutting down server...")

	// Give the server 5 seconds to finish outstanding requests
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Fatal("Server forced to shutdown:", err)
	}

	log.Println("Server exiting")
}

func produceTrascation(txn Transaction) {
	alarmKafkaTopic := EbzTxnsTopic

	txnBytes, err := json.Marshal(txn)
	if err != nil {
		log.Fatalln(err)
	}
	err = prod.Produce(&kafka.Message{
		TopicPartition: kafka.TopicPartition{Topic: &alarmKafkaTopic, Partition: kafka.PartitionAny},
		Value:          txnBytes,
	}, nil)
	if err != nil {
		panic(err)
	}
}



// SELECT CASE WHEN COALESCE(sum(amount), 0) > CAST(LOOKUP('-1', 'GMVLookupTable') AS DOUBLE) THEN TRUE ELSE FALSE END AS is_greater_than_lookup FROM EbzTxnsTopic WHERE ((TIMESTAMP_TO_MILLIS("__time") > TIMESTAMP_TO_MILLIS(CURRENT_TIMESTAMP) - CAST(LOOKUP('-1', 'shortTimePeriodLookupTable') AS BIGINT)*1000));

