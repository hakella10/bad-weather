package com.example.ai.controller;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;

import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

import com.example.ai.model.GreetingRequest;
import com.example.ai.model.GreetingResponse;

@RestController
public class BadWeatherController {
    
    private final Logger LOGGER = LogManager.getLogger(this.getClass());
    private final String GOOD_MORNING = "Good Morning !";
   
    @Value("${range}")
    private String range;

    @Value("${threshold}")
    private String threshold;

    @GetMapping("/hello")
    public ResponseEntity<GreetingResponse> sayHello(@RequestParam(required = false) String user ) {
        String msg = "Hello, ";
        
        if (user == null || user.trim().equals("")) {
            msg += "Anonymous";
        }
        else{
            msg += user;
        }

        return new ResponseEntity<>(GreetingResponse.builder().message(msg).build(), HttpStatus.OK);
        
    }

    @PostMapping("/greet")
    public HttpEntity<GreetingResponse> greetUser(@RequestBody GreetingRequest request) {
        
        if (request == null || request.getUser() == null ){
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }

        StringBuilder msg = new StringBuilder();
        if ("".equals(request.getUser().trim())) {
            msg.append(this.GOOD_MORNING);
        }
        else{
            msg.append(request.getUser());
            msg.append(",");
            msg.append(this.GOOD_MORNING);
        }
        return new ResponseEntity<>(GreetingResponse.builder().message(msg.toString()).build(), HttpStatus.OK);
    }
    
    @PostMapping("/howru")
    public HttpEntity<GreetingResponse> howAreYou(@RequestBody GreetingRequest request) {
        
        if (request == null || request.getUser() == null ){
            return new ResponseEntity<>(HttpStatus.BAD_REQUEST);
        }

        StringBuilder msg = new StringBuilder();
        if ("".equals(request.getUser().trim())) {
            msg.append(this.GOOD_MORNING);
        }
        else{
            msg.append(request.getUser());
            msg.append(",");
            msg.append(this.GOOD_MORNING);
        }

        try{

            Integer intRange = Integer.parseInt(this.range);
            Integer intThreshold = Integer.parseInt(this.threshold);

            if ( (Math.random()*intRange) < intThreshold ) {
                LOGGER.info("Randomness is less than threshold");
                msg.append("I am fine. Thank you.");
                return new ResponseEntity<>(GreetingResponse.builder().message(msg.toString()).build(), HttpStatus.OK);
            }
            else{
                LOGGER.info("Randomness is more than threshold");
                throw new RuntimeException("Sorry, Weather is bad !");
            }
        }
        catch(NumberFormatException nfe){
            LOGGER.error(nfe);
            return new ResponseEntity<>(HttpStatus.INTERNAL_SERVER_ERROR);
        }
        catch(RuntimeException re){
            LOGGER.error(re);
            msg.append(re.getMessage());
            return new ResponseEntity<>(GreetingResponse.builder().message(msg.toString()).build(), HttpStatus.EXPECTATION_FAILED);
        }

    }
}
