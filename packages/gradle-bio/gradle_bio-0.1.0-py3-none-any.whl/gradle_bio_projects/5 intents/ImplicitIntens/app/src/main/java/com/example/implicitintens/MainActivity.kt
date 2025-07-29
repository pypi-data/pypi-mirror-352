package com.example.implicitintens

import android.content.Intent
import android.net.Uri
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val searchButton = findViewById<Button>(R.id.searchButton)
        searchButton.setOnClickListener {
            val query = "computer"
            val uri = Uri.parse("https://www.google.com/search?q=$query")
            val intent = Intent(Intent.ACTION_VIEW, uri)

// Force Chrome
            intent.setPackage("com.android.chrome")

            if (intent.resolveActivity(packageManager) != null) {
                startActivity(intent)
            } else {
                // Chrome not installed, fallback to any browser
                val fallbackIntent = Intent(Intent.ACTION_VIEW, uri)
                startActivity(fallbackIntent)
            }

        }
    }
}