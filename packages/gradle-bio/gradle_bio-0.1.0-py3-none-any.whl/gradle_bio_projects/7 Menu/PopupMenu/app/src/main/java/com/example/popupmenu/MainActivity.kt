package com.example.popupmenu

import android.support.v7.app.AppCompatActivity
import android.os.Bundle
import android.widget.Button
import android.widget.PopupMenu
import android.widget.Toast

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val B1 = findViewById<Button>(R.id.B1)
        B1.setOnClickListener {
            val popupMenu: PopupMenu = PopupMenu(this, B1)
            popupMenu.menuInflater.inflate(R.menu.popup_menu, popupMenu.menu)
            popupMenu.setOnMenuItemClickListener(PopupMenu.OnMenuItemClickListener { item
                ->
                when (item.itemId) {
                    R.id.item1 ->
                        Toast.makeText(
                            this@MainActivity,
                            "You Clicked : " + item.title,Toast.LENGTH_SHORT).show()
                    R.id.item2 ->
                        Toast.makeText(
                            this@MainActivity,
                            "You Clicked : " + item.title,Toast.LENGTH_SHORT).show()
                    R.id.item3 ->
                        Toast.makeText(this@MainActivity,"You Clicked : " +
                                item.title,Toast.LENGTH_SHORT).show()
                }
                true
            })
            popupMenu.show()
        }
    }
}