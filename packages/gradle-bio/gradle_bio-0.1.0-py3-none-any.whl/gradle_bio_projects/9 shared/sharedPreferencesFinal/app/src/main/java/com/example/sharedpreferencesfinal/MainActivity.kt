package com.example.sharedpreferencesfinal

import android.content.Context
import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val name = findViewById<EditText>(R.id.ed1)
        val password = findViewById<EditText>(R.id.ed2)
        val save = findViewById<Button>(R.id.b1)
        val load = findViewById<Button>(R.id.b2)
        val clear = findViewById<Button>(R.id.b3)
        val del = findViewById<Button>(R.id.b4)
        val sharedPref = getSharedPreferences("addName", Context.MODE_PRIVATE)

        save.setOnClickListener {
            val edit = sharedPref.edit()
            edit.putString("name", name.text.toString())
            edit.putString("password", password.text.toString())
            edit.commit()
            Toast.makeText(this, "Data Saved", Toast.LENGTH_LONG).show()
        }

        load.setOnClickListener {
            val getname = sharedPref.getString("name", "default value")
            val getpass = sharedPref.getString("password", "default value")
            // Load data into EditText fields
            name.setText(getname)
            password.setText(getpass)
            Toast.makeText(this, "$getname $getpass", Toast.LENGTH_LONG).show()
        }

        clear.setOnClickListener {
            val edit = sharedPref.edit()
            edit.remove("password")
            edit.commit()
            // Clear the password EditText field
            password.setText("")
            Toast.makeText(this, "Password cleared", Toast.LENGTH_LONG).show()
        }

        del.setOnClickListener {
            val edit = sharedPref.edit()
            edit.clear()
            edit.commit()
            // Clear both EditText fields
            name.setText("")
            password.setText("")
            Toast.makeText(this, "All data deleted", Toast.LENGTH_LONG).show()
        }
    }
}