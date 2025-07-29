package com.example.newexplicitintent

import android.content.Intent
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
//Explicit Intent
        val explicitButton=findViewById<Button>(R.id.ExplicitButton)
        explicitButton.setOnClickListener {
            val explicitIntent= Intent(this, SecondActivity::class.java)
            startActivity(explicitIntent)
            finish()
        }
    }
}