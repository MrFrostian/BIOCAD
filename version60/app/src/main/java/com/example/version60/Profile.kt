package com.example.projectvesion

import android.content.Intent
import android.os.Bundle
import androidx.fragment.app.Fragment
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import com.example.version60.ChatBot
import com.example.version60.R



class Profile : Fragment() {



    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_profile, container, false)

    }
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val btChat: Button = view.findViewById(R.id.chatBot)
        btChat.setOnClickListener {
            // Создайте Intent, указывающий на ваш ChatBot Activity
            val intent = Intent(requireContext(), ChatBot::class.java)

            // Запустите Activity
            startActivity(intent)
        }


    }
    companion object {

        @JvmStatic
        fun newInstance(param1: String, param2: String) = Profile()
    }
}