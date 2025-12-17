import * as THREE from 'three'
import React, { useEffect, useMemo, useRef, useState } from 'react'
import { useGraph, useFrame } from '@react-three/fiber'
import { useGLTF, useAnimations } from '@react-three/drei'
import { SkeletonUtils } from 'three-stdlib'
import { Lipsync } from 'wawa-lipsync'

export function Ziva({ audio, playTick, ...props }) {
  const group = useRef(null)

  // Avatar model
  const { scene } = useGLTF('/models/Ziva.glb')
  const clone = useMemo(() => SkeletonUtils.clone(scene), [scene])
  const { nodes, materials } = useGraph(clone)

  // Animations (Idle, etc.)
  const { animations: clips } = useGLTF('/models/Animations.glb')

  useMemo(() => {
    if (!clips) return

    clips.forEach((clip) => {
      if (!clip.tracks) return

      // Filter out problematic tracks and rename bones from Mixamo
      clip.tracks = clip.tracks.filter((track) => {
        const name = track.name.toLowerCase()
        return !name.includes('end') && !name.includes('nub') && !name.includes('armature')
      })

      clip.tracks.forEach((track) => {
        track.name = track.name.replace('mixamorig', '')
      })
    })
  }, [clips])

  const { actions, names } = useAnimations(clips || [], group)
  const [idleName, setIdleName] = useState(null)

  // Pick an Idle animation and loop it
  useEffect(() => {
    if (!names || names.length === 0) return
    const foundIdle = names.find((n) => n.toLowerCase().includes('idle')) || names[0]
    setIdleName(foundIdle)
  }, [names])

  useEffect(() => {
    if (!idleName || !actions[idleName]) return

    const action = actions[idleName]
    action.reset().fadeIn(0.5).play()
    action.setLoop(THREE.LoopRepeat, Infinity)

    return () => {
      action.fadeOut(0.5)
    }
  }, [idleName, actions])

  // Lipsync setup using shared Audio element from Show
  const lipsyncRef = useRef(null)

  useEffect(() => {
    if (!audio) return

    if (!lipsyncRef.current) {
      lipsyncRef.current = new Lipsync()
    }

    lipsyncRef.current.connectAudio(audio)

    return () => {
      // Lipsync library handles cleanup internally; nothing special here
    }
  }, [audio, playTick])

  // Simple blinking
  const [blink, setBlink] = useState(false)

  useEffect(() => {
    let timeout
    const loop = () => {
      timeout = setTimeout(() => {
        setBlink(true)
        setTimeout(() => {
          setBlink(false)
          loop()
        }, 150)
      }, THREE.MathUtils.randInt(1200, 4000))
    }
    loop()
    return () => clearTimeout(timeout)
  }, [])

  // Drive morph targets for visemes + blinking each frame
  useFrame(() => {
    const lipsync = lipsyncRef.current
    const head = nodes.Wolf3D_Head
    const teeth = nodes.Wolf3D_Teeth

    if (!head || !teeth || !lipsync || !audio) return

    const audioPlaying = !audio.paused && !audio.ended

    if (audioPlaying) {
      lipsync.processAudio()
    }

    const currentViseme = lipsync.viseme

    Object.keys(head.morphTargetDictionary || {}).forEach((key) => {
      const headIndex = head.morphTargetDictionary[key]
      const teethIndex = teeth.morphTargetDictionary[key]
      if (headIndex === undefined) return

      let targetValue = 0

      // Blinking
      if (key === 'eyeBlinkLeft' || key === 'eyeBlinkRight') {
        targetValue = blink ? 1 : 0
      }

      // Viseme-based mouth shapes while audio is playing
      if (audioPlaying && key.startsWith('viseme_')) {
        if (key === currentViseme) {
          targetValue = 1.0
        }
      }

      const lerpSpeed = audioPlaying && key.startsWith('viseme_') ? 0.5 : 0.25

      head.morphTargetInfluences[headIndex] = THREE.MathUtils.lerp(
        head.morphTargetInfluences[headIndex] || 0,
        targetValue,
        lerpSpeed
      )

      if (teethIndex !== undefined) {
        teeth.morphTargetInfluences[teethIndex] = THREE.MathUtils.lerp(
          teeth.morphTargetInfluences[teethIndex] || 0,
          targetValue,
          lerpSpeed
        )
      }
    })
  })

  return (
    <group ref={group} {...props} dispose={null}>
      <primitive object={nodes.Hips} />
      <skinnedMesh 
        geometry={nodes.Wolf3D_Hair.geometry} 
        material={materials.Wolf3D_Hair} 
        skeleton={nodes.Wolf3D_Hair.skeleton} 
      />
      <skinnedMesh 
        geometry={nodes.Wolf3D_Outfit_Top.geometry} 
        material={materials.Wolf3D_Outfit_Top} 
        skeleton={nodes.Wolf3D_Outfit_Top.skeleton} 
      />
      <skinnedMesh 
        geometry={nodes.Wolf3D_Outfit_Bottom.geometry} 
        material={materials.Wolf3D_Outfit_Bottom} 
        skeleton={nodes.Wolf3D_Outfit_Bottom.skeleton} 
      />
      <skinnedMesh 
        geometry={nodes.Wolf3D_Outfit_Footwear.geometry} 
        material={materials.Wolf3D_Outfit_Footwear} 
        skeleton={nodes.Wolf3D_Outfit_Footwear.skeleton} 
      />
      <skinnedMesh 
        geometry={nodes.Wolf3D_Body.geometry} 
        material={materials.Wolf3D_Body} 
        skeleton={nodes.Wolf3D_Body.skeleton} 
      />
      <skinnedMesh 
        name="EyeLeft" 
        geometry={nodes.EyeLeft.geometry} 
        material={materials.Wolf3D_Eye} 
        skeleton={nodes.EyeLeft.skeleton} 
        morphTargetDictionary={nodes.EyeLeft.morphTargetDictionary} 
        morphTargetInfluences={nodes.EyeLeft.morphTargetInfluences} 
      />
      <skinnedMesh 
        name="EyeRight" 
        geometry={nodes.EyeRight.geometry} 
        material={materials.Wolf3D_Eye} 
        skeleton={nodes.EyeRight.skeleton} 
        morphTargetDictionary={nodes.EyeRight.morphTargetDictionary} 
        morphTargetInfluences={nodes.EyeRight.morphTargetInfluences} 
      />
      <skinnedMesh 
        name="Wolf3D_Head" 
        geometry={nodes.Wolf3D_Head.geometry} 
        material={materials.Wolf3D_Skin} 
        skeleton={nodes.Wolf3D_Head.skeleton} 
        morphTargetDictionary={nodes.Wolf3D_Head.morphTargetDictionary} 
        morphTargetInfluences={nodes.Wolf3D_Head.morphTargetInfluences} 
      />
      <skinnedMesh 
        name="Wolf3D_Teeth" 
        geometry={nodes.Wolf3D_Teeth.geometry} 
        material={materials.Wolf3D_Teeth} 
        skeleton={nodes.Wolf3D_Teeth.skeleton} 
        morphTargetDictionary={nodes.Wolf3D_Teeth.morphTargetDictionary} 
        morphTargetInfluences={nodes.Wolf3D_Teeth.morphTargetInfluences} 
      />
    </group>
  )
}

useGLTF.preload('/models/Ziva.glb')
useGLTF.preload('/models/Animations.glb')
