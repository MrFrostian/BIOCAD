package com.example.version60

import android.content.Intent
import android.os.Bundle
import android.telecom.Call
import android.widget.Button
import android.widget.EditText
import android.widget.ImageView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContentProviderCompat.requireContext
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.tracing.perfetto.handshake.protocol.Response
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.Callback
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import okio.IOException
import okhttp3.*
import kotlinx.coroutines.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject


class ChatBot : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_chat_bot)
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main)) { v, insets ->
            val systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom)
            insets
        }

        // API Token
        val apiToken = "b5721c78-875d-4608-a482-72a6bc62122b"

        // URL вашего Flask-бэка
        val apiUrl = "http://<176.214.202.28>:5000/askQuestion"  // Замените <ваш IP> на реальный IP-адрес сервера

        val btback: Button = findViewById(R.id.back)
        btback.setOnClickListener {
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)
        }

        val inputMessages: EditText = findViewById(R.id.inputMessage)
        val imageView: ImageView = findViewById(R.id.sendMessadge)
        imageView.setOnClickListener {
            val message = inputMessages.text.toString().trim()
            if (message.isNotEmpty()) {
                CoroutineScope(Dispatchers.IO).launch {
                    val client = OkHttpClient()

                    // Создаем JSON-запрос
                    val json = JSONObject()
                    json.put("question", message)


                    val requestBody = json.toString().toRequestBody("application/json".toMediaTypeOrNull())

                    // Создаем запрос
                    val request = Request.Builder()
                        .url(apiUrl)
                        .post(requestBody)
                        .addHeader("Authorization", "Bearer $apiToken")
                        .build()

                    // Выполняем запрос
                    client.newCall(request).enqueue(object : Callback {
                        override fun onFailure(call: okhttp3.Call, e: java.io.IOException) {
                            // Обработка ошибки
                            runOnUiThread {
                                Toast.makeText(this@ChatBot, "Ошибка отправки сообщения", Toast.LENGTH_SHORT).show()
                            }
                        }

                        override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                            runOnUiThread {
                                if (response.isSuccessful) { // Проверка успешного ответа
                                    val responseBody = response.body?.string()
                                    responseBody?.let {
                                        val jsonResponse = JSONObject(it)
                                        val botResponse = jsonResponse.optString("answer", "Нет ответа")

                                        // Установка ответа бота в поле
                                        val botsMessage: EditText = findViewById(R.id.botsMessedge)
                                        botsMessage.setText(botResponse)
                                    }
                                    inputMessages.text.clear()
                                } else {
                                    Toast.makeText(this@ChatBot, "Ошибка: ${response.message}", Toast.LENGTH_SHORT).show()
                                }
                            }
                            response.body?.close()
                        }
                    })
                }
            } else {
                Toast.makeText(this, "Введите сообщение", Toast.LENGTH_SHORT).show()
            }
        }
    }
}