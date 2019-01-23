/* https://github.com/rikschennink/shiny */
shiny('.shiny', {
    // type of shiny to render,
    // 'background', 'border', or 'text'
    type: 'background',
    gradient: {

        // type of gradient
        // 'linear' or 'radial'
        type: 'radial',

        // angle of gradient when type is linear
        angle: '110deg',

        // flip axis movement
        flip: {
            x: true,
            y: false
        },

        // colors to use
        colors: [
            // offset, color, opacity
            // ! don't pass rgba or hsla colors, supply the opacity seperately
            [0, '#fff', 1], // white at 0%
            [1, '#fff', 0], // to fully transparent white at 100%
        ]

    },

    // optional pattern fill
    pattern: {
        type: 'noise', // only 'noise' for now
        opacity: .5
    }
});
