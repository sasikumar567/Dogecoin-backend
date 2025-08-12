package com.sasikumar.DogecoinPriceForecasting.Controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.sasikumar.DogecoinPriceForecasting.Model.Forecast;
import com.sasikumar.DogecoinPriceForecasting.Service.GiveForecast;
@RestController
@RequestMapping("dogecoin")
@CrossOrigin
public class Controller1 {
	@Autowired
	GiveForecast service;
	
	@GetMapping("forecast")
	public List<Forecast> forcast(){
		return service.getForecast();
		
	}

}
